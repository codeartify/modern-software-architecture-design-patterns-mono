package com.workshop.architecture.fitness.membership.business;

import com.workshop.architecture.fitness.customer.CustomerEntity;
import com.workshop.architecture.fitness.customer.CustomerRepository;
import com.workshop.architecture.fitness.email.InMemoryEmailService;
import com.workshop.architecture.fitness.membership.infrastructure.MembershipBillingReferenceEntity;
import com.workshop.architecture.fitness.membership.infrastructure.MembershipEntity;
import com.workshop.architecture.fitness.membership.infrastructure.MembershipRepository;
import com.workshop.architecture.fitness.plan.PlanRepository;
import jakarta.transaction.Transactional;
import org.jspecify.annotations.NonNull;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.Period;
import java.util.UUID;

@Service
public class MembershipService {
    private final MembershipRepository membershipRepository;
    private final CustomerRepository customerRepository;
    private final PlanRepository planRepository;
    private final InMemoryEmailService emailService;
    private final String billingSenderEmailAddress;
    private final InvoiceService invoiceService;


    public MembershipService(
            MembershipRepository membershipRepository,
            CustomerRepository customerRepository,
            PlanRepository planRepository,
            InMemoryEmailService emailService,
            @Value("${workshop.billing.sender-email-address}") String billingSenderEmailAddress,
            InvoiceService invoiceService
    ) {
        this.membershipRepository = membershipRepository;
        this.customerRepository = customerRepository;
        this.planRepository = planRepository;
        this.emailService = emailService;
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


        var email = emailDetails.emailTemplate().formatted(
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

        System.out.println(email);

        emailService.send(email);
    }

}
