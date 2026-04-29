package com.workshop.architecture.fitness.membership;

import com.workshop.architecture.fitness.customer.CustomerEntity;
import com.workshop.architecture.fitness.customer.CustomerRepository;
import com.workshop.architecture.fitness.email.InMemoryEmailService;
import com.workshop.architecture.fitness.external_invoice_provider.ExternalInvoiceProviderResponse;
import com.workshop.architecture.fitness.external_invoice_provider.ExternalInvoiceProviderStatus;
import com.workshop.architecture.fitness.external_invoice_provider.ExternalInvoiceProviderUpsertRequest;
import com.workshop.architecture.fitness.plan.PlanEntity;
import com.workshop.architecture.fitness.plan.PlanRepository;
import jakarta.validation.Valid;
import java.time.Instant;
import java.time.LocalDate;
import java.time.Period;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClient;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/memberships")
public class MembershipController {

    private final MembershipRepository membershipRepository;
    private final MembershipBillingReferenceRepository billingReferenceRepository;
    private final CustomerRepository customerRepository;
    private final PlanRepository planRepository;
    private final InMemoryEmailService emailService;
    private final RestClient restClient;
    private final String billingSenderEmailAddress;

    public MembershipController(
            MembershipRepository membershipRepository,
            MembershipBillingReferenceRepository billingReferenceRepository,
            CustomerRepository customerRepository,
            PlanRepository planRepository,
            InMemoryEmailService emailService,
            RestClient.Builder restClientBuilder,
            @Value("${workshop.external-invoice-provider.base-url}") String externalInvoiceProviderBaseUrl,
            @Value("${workshop.billing.sender-email-address}") String billingSenderEmailAddress
    ) {
        this.membershipRepository = membershipRepository;
        this.billingReferenceRepository = billingReferenceRepository;
        this.customerRepository = customerRepository;
        this.planRepository = planRepository;
        this.emailService = emailService;
        this.restClient = restClientBuilder.baseUrl(externalInvoiceProviderBaseUrl).build();
        this.billingSenderEmailAddress = billingSenderEmailAddress;
    }

    @GetMapping
    List<MembershipResponse> listMemberships() {
        return membershipRepository.findAll().stream()
                .map(MembershipResponse::fromEntity)
                .toList();
    }

    @GetMapping("/{membershipId}")
    MembershipResponse getMembership(@PathVariable String membershipId) {
        MembershipEntity membership = membershipRepository.findById(UUID.fromString(membershipId))
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Membership %s was not found".formatted(membershipId)
                ));

        return MembershipResponse.fromEntity(membership);
    }

    @PostMapping("/activate")
    ActivateMembershipResponse activateMembership(@Valid @RequestBody ActivateMembershipRequest request) {
        CustomerEntity customer;
        PlanEntity plan;
        MembershipEntity membership;
        MembershipBillingReferenceEntity billingReference;
        String email;
        String invoiceId;
        String externalInvoiceId;
        Instant now;
        LocalDate invoiceDueDate;
        LocalDate startDate;
        LocalDate endDate;

        customer = customerRepository.findById(UUID.fromString(request.customerId()))
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Customer %s was not found".formatted(request.customerId())
                ));

        plan = planRepository.findById(UUID.fromString(request.planId()))
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Plan %s was not found".formatted(request.planId())
                ));

        startDate = LocalDate.now();
        endDate = startDate.plusMonths(plan.getDurationInMonths());

        if (Period.between(customer.getDateOfBirth(), startDate).getYears() < 18
                && !Boolean.TRUE.equals(request.signedByCustodian())) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "Customers younger than 18 require signedByCustodian=true"
            );
        }

        membership = membershipRepository.save(new MembershipEntity(
                UUID.randomUUID(),
                request.customerId(),
                request.planId(),
                plan.getPrice().intValue(),
                plan.getDurationInMonths(),
                "ACTIVE",
                null,
                startDate,
                endDate
        ));

        invoiceId = UUID.randomUUID().toString();
        invoiceDueDate = LocalDate.now().plusDays(30);
        now = Instant.now();


        var externalInvoice = restClient.post()
                .uri("/api/shared/external-invoice-provider/invoices")
                .contentType(MediaType.APPLICATION_JSON)
                .body(new ExternalInvoiceProviderUpsertRequest(
                        request.customerId(),
                        membership.getId().toString(),
                        membership.getPlanPrice(),
                        "CHF",
                        invoiceDueDate,
                        ExternalInvoiceProviderStatus.OPEN,
                        "Membership invoice for %s".formatted(plan.getTitle()),
                        invoiceId,
                        Map.of(
                                "exercise", "membership",
                                "planId", membership.getPlanId()
                        )
                ))
                .retrieve()
                .body(ExternalInvoiceProviderResponse.class);

        externalInvoiceId = externalInvoice == null ? invoiceId : externalInvoice.invoiceId();

        billingReference = billingReferenceRepository.save(new MembershipBillingReferenceEntity(
                UUID.randomUUID(),
                membership.getId(),
                externalInvoiceId,
                invoiceId,
                invoiceDueDate,
                "OPEN",
                now,
                now
        ));

        email = """
                |
                |To: %s
                |From: %s
                |Subject: Your Membership Invoice %s
                |
                |Dear customer,
                |
                |Thank you for your membership.
                |
                |Please find your invoice details below:
                |Invoice ID: %s
                |Amount Due: CHF %s
                |Due Date: %s
                |
                |Attachment: invoice-%s.pdf
                |
                |Kind regards,
                |Codeartify Billing
                |
                """.formatted(
                customer.getEmailAddress(),
                billingSenderEmailAddress,
                invoiceId,
                invoiceId,
                membership.getPlanPrice(),
                invoiceDueDate,
                invoiceId
        ).replace("\n|", "\n").trim();

        System.out.println(email);

        emailService.send(email);

        return new ActivateMembershipResponse(
                billingReference.getMembershipId().toString(),
                membership.getCustomerId(),
                membership.getPlanId(),
                membership.getPlanPrice(),
                membership.getPlanDuration(),
                membership.getStatus(),
                membership.getStartDate(),
                membership.getEndDate(),
                billingReference.getExternalInvoiceReference(),
                billingReference.getExternalInvoiceId(),
                billingReference.getDueDate()
        );
    }

    @PostMapping("/suspend-overdue")
    SuspendOverdueMembershipsResponse suspendOverdueMemberships(
            @RequestBody(required = false) SuspendOverdueMembershipsRequest request
    ) {
        Instant checkedAt = request == null || request.checkedAt() == null ? Instant.now() : request.checkedAt();
        LocalDate checkedAtDate = checkedAt.atZone(ZoneOffset.UTC).toLocalDate();
        List<MembershipEntity> memberships = membershipRepository.findAll();
        List<MembershipBillingReferenceEntity> openBillingReferences = billingReferenceRepository.findByStatus("OPEN");
        List<String> suspendedMembershipIds = new ArrayList<>();
        int checkedMemberships = 0;

        for (MembershipEntity membership : memberships) {
            if (!"ACTIVE".equals(membership.getStatus())) {
                continue;
            }

            checkedMemberships++;

            MembershipBillingReferenceEntity overdueBillingReference = openBillingReferences.stream()
                    .filter(billingReference -> membership.getId().equals(billingReference.getMembershipId()))
                    .filter(billingReference -> billingReference.getDueDate().isBefore(checkedAtDate))
                    .findFirst()
                    .orElse(null);

            if (overdueBillingReference == null) {
                continue;
            }

            if (!membership.isSuspendedForNonPayment()) {
                membership.suspendForNonPayment();
                membershipRepository.save(membership);
                suspendedMembershipIds.add(membership.getId().toString());
            }
        }

        return new SuspendOverdueMembershipsResponse(
                checkedAt,
                checkedMemberships,
                suspendedMembershipIds
        );
    }

    @PostMapping("/payment-received")
    ResponseEntity<PaymentReceivedResponse> paymentReceived(@RequestBody PaymentReceivedRequest request) {
        MembershipBillingReferenceEntity billingReference;
        MembershipEntity membership;
        Instant paidAt;
        String previousMembershipStatus;
        String newMembershipStatus;
        String message;
        boolean reactivated;

        if ((request.externalInvoiceId() == null || request.externalInvoiceId().isBlank())
                && (request.externalInvoiceReference() == null || request.externalInvoiceReference().isBlank())
                && (request.membershipId() == null || request.membershipId().isBlank())) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "At least one invoice or membership identifier must be provided"
            );
        }

        if (request.externalInvoiceId() != null && !request.externalInvoiceId().isBlank()) {
            billingReference = billingReferenceRepository.findByExternalInvoiceId(request.externalInvoiceId())
                    .orElse(null);
        } else {
            billingReference = null;
        }

        if (billingReference == null
                && request.externalInvoiceReference() != null
                && !request.externalInvoiceReference().isBlank()) {
            billingReference = billingReferenceRepository.findByExternalInvoiceReference(
                    request.externalInvoiceReference()
            ).orElse(null);
        }

        if (billingReference == null && request.membershipId() != null && !request.membershipId().isBlank()) {
            billingReference = billingReferenceRepository.findByMembershipId(UUID.fromString(request.membershipId()))
                    .stream()
                    .findFirst()
                    .orElse(null);
        }

        if (billingReference == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "No billing reference was found");
        }

        paidAt = request.paidAt() == null ? Instant.now() : request.paidAt();
        message = billingReference.isPaid()
                ? "Payment was already recorded; membership status unchanged"
                : "Payment recorded; membership status unchanged";

        if (!billingReference.isPaid()) {
            billingReference.markPaid(paidAt);
            billingReference = billingReferenceRepository.save(billingReference);
        }

        UUID billingReferenceMembershipId = billingReference.getMembershipId();

        membership = membershipRepository.findById(billingReferenceMembershipId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Membership %s was not found".formatted(billingReferenceMembershipId)
                ));

        previousMembershipStatus = membership.getStatus();
        newMembershipStatus = membership.getStatus();
        reactivated = false;

        if (membership.isSuspendedForNonPayment()) {
            if (!paidAt.atZone(ZoneOffset.UTC).toLocalDate().isAfter(membership.getEndDate())) {
                membership.reactivateAfterPayment();
                membership = membershipRepository.save(membership);
                newMembershipStatus = membership.getStatus();
                message = "Payment recorded; membership reactivated";
                reactivated = true;
            }
        }

        return ResponseEntity.ok(new PaymentReceivedResponse(
                paidAt,
                membership.getId().toString(),
                billingReference.getId().toString(),
                previousMembershipStatus,
                newMembershipStatus,
                reactivated,
                message
        ));
    }
}
