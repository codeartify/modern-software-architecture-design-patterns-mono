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

    @PostMapping("/{membershipId}/pause")
    PauseMembershipResponse pauseMembership(
            @PathVariable String membershipId,
            @RequestBody PauseMembershipRequest request
    ) {
        MembershipEntity membership;
        String previousStatus;
        LocalDate previousEndDate;

        if (request.pauseStartDate() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "pauseStartDate is required");
        }

        if (request.pauseEndDate() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "pauseEndDate is required");
        }

        if (request.pauseEndDate().isBefore(request.pauseStartDate())) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "pauseEndDate must not be before pauseStartDate"
            );
        }

        membership = membershipRepository.findById(UUID.fromString(membershipId))
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Membership %s was not found".formatted(membershipId)
                ));

        if (!membership.isActive()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Only active memberships can be paused");
        }

        if (membership.getEndDate().isBefore(LocalDate.now())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Expired memberships cannot be paused");
        }

        previousStatus = membership.getStatus();
        previousEndDate = membership.getEndDate();

        membership.pause(request.pauseStartDate(), request.pauseEndDate(), request.reason());
        membership = membershipRepository.save(membership);

        return new PauseMembershipResponse(
                membership.getId().toString(),
                previousStatus,
                membership.getStatus(),
                membership.getPauseStartDate(),
                membership.getPauseEndDate(),
                previousEndDate,
                membership.getEndDate(),
                membership.getPauseReason(),
                "Membership paused"
        );
    }

    @PostMapping("/{membershipId}/resume")
    ResumeMembershipResponse resumeMembership(
            @PathVariable String membershipId,
            @RequestBody(required = false) ResumeMembershipRequest request
    ) {
        MembershipEntity membership;
        Instant resumedAt;
        String previousStatus;
        LocalDate previousPauseStartDate;
        LocalDate previousPauseEndDate;
        String reason;

        membership = membershipRepository.findById(UUID.fromString(membershipId))
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Membership %s was not found".formatted(membershipId)
                ));

        if (!membership.isPaused()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Only paused memberships can be resumed");
        }

        if (membership.getEndDate().isBefore(LocalDate.now())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Expired memberships cannot be resumed");
        }

        resumedAt = request == null || request.resumedAt() == null ? Instant.now() : request.resumedAt();
        reason = request == null ? null : request.reason();
        previousStatus = membership.getStatus();
        previousPauseStartDate = membership.getPauseStartDate();
        previousPauseEndDate = membership.getPauseEndDate();

        membership.resumeAfterPause();
        membership = membershipRepository.save(membership);

        return new ResumeMembershipResponse(
                membership.getId().toString(),
                previousStatus,
                membership.getStatus(),
                resumedAt,
                previousPauseStartDate,
                previousPauseEndDate,
                membership.getEndDate(),
                reason,
                "Membership resumed"
        );
    }

    @PostMapping("/{membershipId}/cancel")
    CancelMembershipResponse cancelMembership(
            @PathVariable String membershipId,
            @RequestBody(required = false) CancelMembershipRequest request
    ) {
        MembershipEntity membership;
        Instant cancelledAt;
        String previousStatus;
        String reason;

        membership = membershipRepository.findById(UUID.fromString(membershipId))
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Membership %s was not found".formatted(membershipId)
                ));

        if (membership.isCancelled()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Membership is already cancelled");
        }

        cancelledAt = request == null || request.cancelledAt() == null ? Instant.now() : request.cancelledAt();
        reason = request == null ? null : request.reason();
        previousStatus = membership.getStatus();

        membership.cancel(cancelledAt, reason);
        membership = membershipRepository.save(membership);

        return new CancelMembershipResponse(
                membership.getId().toString(),
                previousStatus,
                membership.getStatus(),
                membership.getCancelledAt(),
                membership.getCancellationReason(),
                "Membership cancelled"
        );
    }

    @PostMapping("/{membershipId}/extend")
    ExtendMembershipResponse extendMembership(
            @PathVariable String membershipId,
            @RequestBody ExtendMembershipRequest request
    ) {
        MembershipEntity membership;
        MembershipBillingReferenceEntity billingReference;
        int additionalMonths = request.additionalMonths() == null ? 0 : request.additionalMonths();
        int additionalDays = request.additionalDays() == null ? 0 : request.additionalDays();
        boolean billable = Boolean.TRUE.equals(request.billable());
        LocalDate previousEndDate;
        String invoiceId;
        String externalInvoiceId;
        LocalDate invoiceDueDate;
        Instant now;

        membership = membershipRepository.findById(UUID.fromString(membershipId))
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Membership %s was not found".formatted(membershipId)
                ));

        if (membership.isCancelled()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Cancelled memberships cannot be extended");
        }

        if (membership.getEndDate().isBefore(LocalDate.now())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Expired memberships cannot be extended");
        }

        if (additionalMonths < 0 || additionalDays < 0 || (additionalMonths == 0 && additionalDays == 0)) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Extension duration must be positive");
        }

        if (billable && (request.price() == null || request.price() <= 0)) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Billable extensions require a positive price");
        }

        previousEndDate = membership.getEndDate();
        membership.extendBy(additionalMonths, additionalDays);
        membership = membershipRepository.save(membership);

        if (!billable) {
            return new ExtendMembershipResponse(
                    membership.getId().toString(),
                    membership.getStatus(),
                    previousEndDate,
                    membership.getEndDate(),
                    false,
                    null,
                    null,
                    null,
                    null,
                    "Membership extended"
            );
        }

        invoiceId = UUID.randomUUID().toString();
        invoiceDueDate = LocalDate.now().plusDays(30);
        now = Instant.now();

        var externalInvoice = restClient.post()
                .uri("/api/shared/external-invoice-provider/invoices")
                .contentType(MediaType.APPLICATION_JSON)
                .body(new ExternalInvoiceProviderUpsertRequest(
                        membership.getCustomerId(),
                        membership.getId().toString(),
                        request.price(),
                        "CHF",
                        invoiceDueDate,
                        ExternalInvoiceProviderStatus.OPEN,
                        "Membership extension invoice",
                        invoiceId,
                        Map.of(
                                "exercise", "membership",
                                "membershipId", membership.getId().toString(),
                                "extension", "true"
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

        return new ExtendMembershipResponse(
                membership.getId().toString(),
                membership.getStatus(),
                previousEndDate,
                membership.getEndDate(),
                true,
                billingReference.getId().toString(),
                billingReference.getExternalInvoiceReference(),
                billingReference.getExternalInvoiceId(),
                billingReference.getDueDate(),
                "Membership extended and invoice created"
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

        if (membership.isCancelled()) {
            message = "Payment recorded; membership is cancelled and remains unchanged";
        } else if (membership.isSuspendedForNonPayment()) {
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
