package com.workshop.architecture.fitness.membership.business;

import com.workshop.architecture.fitness.customer.CustomerRepository;
import com.workshop.architecture.fitness.email.InMemoryEmailService;
import com.workshop.architecture.fitness.membership.infrastructure.MembershipBillingReferenceRepository;
import com.workshop.architecture.fitness.membership.infrastructure.MembershipEntity;
import com.workshop.architecture.fitness.membership.infrastructure.MembershipRepository;
import com.workshop.architecture.fitness.plan.PlanRepository;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.time.LocalDate;
import java.time.Period;
import java.util.UUID;

@Service
public class MembershipService {
    private final MembershipRepository membershipRepository;
    private final MembershipBillingReferenceRepository billingReferenceRepository;
    private final CustomerRepository customerRepository;
    private final PlanRepository planRepository;
    private final InMemoryEmailService emailService;
    private final RestClient restClient;
    private final String billingSenderEmailAddress;
    private final InvoiceService invoiceService;


    public MembershipService(
            MembershipRepository membershipRepository,
            MembershipBillingReferenceRepository billingReferenceRepository,
            CustomerRepository customerRepository,
            PlanRepository planRepository,
            InMemoryEmailService emailService,
            RestClient.Builder restClientBuilder,
            @Value("${workshop.external-invoice-provider.base-url}") String externalInvoiceProviderBaseUrl,
            @Value("${workshop.billing.sender-email-address}") String billingSenderEmailAddress,
            InvoiceService invoiceService
    ) {
        this.membershipRepository = membershipRepository;
        this.billingReferenceRepository = billingReferenceRepository;
        this.customerRepository = customerRepository;
        this.planRepository = planRepository;
        this.emailService = emailService;
        this.restClient = restClientBuilder.baseUrl(externalInvoiceProviderBaseUrl).build();
        this.billingSenderEmailAddress = billingSenderEmailAddress;
        this.invoiceService = invoiceService;
    }

    @Transactional
    public ActivateMembershipResult activateMembership(ActivateMembershipInput input) {

        var customer = customerRepository.findById(UUID.fromString(input.customerId()))
                .orElseThrow(() -> new MembershipException(
                        "Customer %s was not found".formatted(input.customerId())
                ));

        var plan = planRepository.findById(UUID.fromString(input.planId()))
                .orElseThrow(() -> new MembershipException(
                        "Plan %s was not found".formatted(input.planId())
                ));

        var startDate = LocalDate.now();
        var endDate = startDate.plusMonths(plan.getDurationInMonths());

        if (Period.between(customer.getDateOfBirth(), startDate).getYears() < 18
                && !Boolean.TRUE.equals(input.signedByCustodian())) {
            throw new MembershipException(
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


        var billingReference = invoiceService.createInvoice(input.customerId(), membership, plan);

        sendEmail(new CustomerActivateMembershipEmail(
                billingReference.getExternalInvoiceId(),
                billingReference.getDueDate(),
                customer.getEmailAddress(),
                membership.getPlanPrice())
        );

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

    private void sendEmail(CustomerActivateMembershipEmail customerActivateMembershipEmail) {
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
                        customerActivateMembershipEmail.emailAddress(),
                        billingSenderEmailAddress,
                        customerActivateMembershipEmail.invoiceId(),
                        customerActivateMembershipEmail.invoiceId(),
                        customerActivateMembershipEmail.planPrice(),
                        customerActivateMembershipEmail.invoiceDueDate(),
                        customerActivateMembershipEmail.invoiceId()
                )
                .replace("\n|", "\n")
                .trim();

        System.out.println(email);

        emailService.send(email);
    }

}
