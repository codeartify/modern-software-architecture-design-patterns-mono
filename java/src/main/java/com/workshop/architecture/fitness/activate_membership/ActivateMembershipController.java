package com.workshop.architecture.fitness.activate_membership;

import com.workshop.architecture.fitness.shared.*;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClient;
import org.springframework.web.server.ResponseStatusException;

import java.time.Instant;
import java.time.LocalDate;
import java.time.Period;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/memberships")
public class ActivateMembershipController {

    private final MembershipRepository membershipRepository;
    private final MembershipBillingReferenceRepository billingReferenceRepository;
    private final CustomerRepository customerRepository;
    private final PlanRepository planRepository;
    private final InMemoryEmailService emailService;
    private final RestClient restClient;
    private final String billingSenderEmailAddress;

    public ActivateMembershipController(
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

}
