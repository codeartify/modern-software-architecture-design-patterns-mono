package com.workshop.architecture.fitness.membership;

import com.workshop.architecture.fitness.customer.CustomerRepository;
import com.workshop.architecture.fitness.email.InMemoryEmailService;
import com.workshop.architecture.fitness.external_invoice_provider.ExternalInvoiceProviderResponse;
import com.workshop.architecture.fitness.external_invoice_provider.ExternalInvoiceProviderStatus;
import com.workshop.architecture.fitness.external_invoice_provider.ExternalInvoiceProviderUpsertRequest;
import com.workshop.architecture.fitness.plan.PlanRepository;
import jakarta.transaction.Transactional;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestClient;
import org.springframework.web.server.ResponseStatusException;

import java.time.Instant;
import java.time.LocalDate;
import java.time.Period;
import java.util.List;
import java.util.Map;
import java.util.UUID;

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
    @Transactional
    ActivateMembershipResponse activateMembership(@Valid @RequestBody ActivateMembershipRequest request) {

        var customer = customerRepository.findById(UUID.fromString(request.customerId()))
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Customer %s was not found".formatted(request.customerId())
                ));

        var plan = planRepository.findById(UUID.fromString(request.planId()))
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Plan %s was not found".formatted(request.planId())
                ));

        var startDate = LocalDate.now();
        var endDate = startDate.plusMonths(plan.getDurationInMonths());

        if (Period.between(customer.getDateOfBirth(), startDate).getYears() < 18
                && !Boolean.TRUE.equals(request.signedByCustodian())) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "Customers younger than 18 require signedByCustodian=true"
            );
        }

        var membership = membershipRepository.save(new MembershipEntity(
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

        var invoiceId = UUID.randomUUID().toString();
        var invoiceDueDate = LocalDate.now().plusDays(30);
        var now = Instant.now();


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

        var externalInvoiceId = externalInvoice == null ? invoiceId : externalInvoice.invoiceId();

        var billingReference = billingReferenceRepository.save(new MembershipBillingReferenceEntity(
                UUID.randomUUID(),
                membership.getId(),
                externalInvoiceId,
                invoiceId,
                invoiceDueDate,
                "OPEN",
                now,
                now
        ));

        var email = """
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
                )
                .replace("\n|", "\n")
                .trim();

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
}
