package com.workshop.architecture.fitness.business;

import com.workshop.architecture.fitness.infrastructure.*;
import com.workshop.architecture.fitness.infrastructure.external_invoice_provider.ExternalInvoiceProviderResponse;
import com.workshop.architecture.fitness.infrastructure.external_invoice_provider.ExternalInvoiceProviderStatus;
import com.workshop.architecture.fitness.infrastructure.external_invoice_provider.ExternalInvoiceProviderUpsertRequest;
import jakarta.transaction.Transactional;
import org.jspecify.annotations.NonNull;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.time.Instant;
import java.time.LocalDate;
import java.time.Period;
import java.util.Map;
import java.util.UUID;

@Service
public class MembershipService {
    private final MembershipRepository membershipRepository;
    private final CustomerRepository customerRepository;
    private final PlanRepository planRepository;
    private final InMemoryEmailService emailService;
    private final String billingSenderEmailAddress;

    private final MembershipBillingReferenceRepository billingReferenceRepository;
    private final RestClient restClient;

    public MembershipService(
            MembershipRepository membershipRepository,
            CustomerRepository customerRepository,
            PlanRepository planRepository,
            InMemoryEmailService emailService,
            @Value("${workshop.billing.sender-email-address}") String billingSenderEmailAddress,
            MembershipBillingReferenceRepository billingReferenceRepository,
            RestClient.Builder restClientBuilder,
            @Value("${workshop.external-invoice-provider.base-url}") String externalInvoiceProviderBaseUrl

    ) {
        this.membershipRepository = membershipRepository;
        this.customerRepository = customerRepository;
        this.planRepository = planRepository;
        this.emailService = emailService;
        this.billingSenderEmailAddress = billingSenderEmailAddress;
        this.billingReferenceRepository = billingReferenceRepository;
        this.restClient = restClientBuilder.baseUrl(externalInvoiceProviderBaseUrl).build();
    }

    @Transactional
    public ActivateMembershipResult activateMembership(ActivateMembershipInput input) {

        var customer = customerRepository.findById(UUID.fromString(input.customerId()))
                .orElseThrow(() -> new CustomerNotFoundException(
                        "Customer %s was not found".formatted(input.customerId())
                ));

        var plan = planRepository.findById(UUID.fromString(input.planId()))
                .orElseThrow(() -> new PlanNotFoundException(
                        "Plan %s was not found".formatted(input.planId())
                ));

        var startDate = LocalDate.now();
        var endDate = startDate.plusMonths(plan.getDurationInMonths());

        if (Period.between(customer.getDateOfBirth(), startDate).getYears() < 18
                && !Boolean.TRUE.equals(input.signedByCustodian())) {
            throw new CustomerTooYoungException(
                    "Customers younger than 18 require signedByCustodian=true"
            );
        }

        var membership = membershipRepository.save(new MembershipEntity(
                UUID.randomUUID(),
                input.customerId(),
                input.planId(),
                plan.getPrice().intValue(),
                plan.getDurationInMonths(),
                "ACTIVE",
                null,
                startDate,
                endDate
        ));


        var invoiceId = UUID.randomUUID().toString();
        var invoiceDueDate = LocalDate.now().plusDays(30);
        var externalInvoiceId = createExternalInvoice(input.customerId(), membership, plan, invoiceDueDate, invoiceId);

        var now = Instant.now();
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

        sendEmail(toEmail(billingReference, customer, membership));

        return new ActivateMembershipResult(
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

    private String createExternalInvoice(String customerId, MembershipEntity membership, PlanEntity plan, LocalDate invoiceDueDate, String invoiceId) {
        var request = new ExternalInvoiceProviderUpsertRequest(
                customerId,
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
        );

        var externalInvoice = restClient.post()
                .uri("/api/shared/external-invoice-provider/invoices")
                .contentType(MediaType.APPLICATION_JSON)
                .body(request)
                .retrieve()
                .body(ExternalInvoiceProviderResponse.class);

        return externalInvoice == null ? invoiceId : externalInvoice.invoiceId();
    }
    private static @NonNull CustomerActivateMembershipEmail toEmail(MembershipBillingReferenceEntity billingReference, CustomerEntity customer, MembershipEntity membership) {
        return new CustomerActivateMembershipEmail(
                billingReference.getExternalInvoiceReference(),
                billingReference.getDueDate(),
                customer.getEmailAddress(),
                membership.getPlanPrice(),
                """
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
                        """);
    }

    private void sendEmail(CustomerActivateMembershipEmail emailDetails) {
        var activationEmail = emailDetails.emailTemplate().formatted(
                        emailDetails.emailAddress(),
                        billingSenderEmailAddress,
                        emailDetails.invoiceId(),
                        emailDetails.invoiceId(),
                        emailDetails.planPrice(),
                        emailDetails.invoiceDueDate(),
                        emailDetails.invoiceId()
                )
                .replace("\n|", "\n")
                .trim();

        System.out.println(activationEmail);

        emailService.send(activationEmail);
    }

}
