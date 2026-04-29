package com.workshop.architecture.fitness.application;

import com.workshop.architecture.fitness.application.port.inbound.ActivateMembership;
import com.workshop.architecture.fitness.application.port.outbound.*;
import com.workshop.architecture.fitness.infrastructure.*;
import com.workshop.architecture.fitness.infrastructure.external_invoice_provider.ExternalInvoiceProviderClient;
import jakarta.transaction.Transactional;
import org.jspecify.annotations.NonNull;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.time.LocalDate;
import java.time.Period;
import java.util.UUID;

@Service
public class MembershipService implements ActivateMembership {
    private final MembershipRepository membershipRepository;
    private final CustomerRepository customerRepository;
    private final PlanRepository planRepository;
    private final InMemoryEmailService emailService;
    private final String billingSenderEmailAddress;
    private final ForFindingCustomers forFindingCustomers;
    private final ForFindingPlans forFindingPlans;
    private final ForStoringMemberships forStoringMemberships;
    private final ForCreatingInvoices forCreatingInvoices;
    private final ForStoringBillingReferences forStoringBillingReferences;
    private final ForSendingEmails forSendingEmails;

    private final MembershipBillingReferenceRepository billingReferenceRepository;
    private final ExternalInvoiceProviderClient externalInvoiceProviderClient;

    public MembershipService(
            MembershipRepository membershipRepository,
            CustomerRepository customerRepository,
            PlanRepository planRepository,
            InMemoryEmailService emailService,
            @Value("${workshop.billing.sender-email-address}") String billingSenderEmailAddress,
            ForFindingCustomers forFindingCustomers,
            ForFindingPlans forFindingPlans,
            ForStoringMemberships forStoringMemberships,
            ForCreatingInvoices forCreatingInvoices,
            ForStoringBillingReferences forStoringBillingReferences,
            ForSendingEmails forSendingEmails,
            MembershipBillingReferenceRepository billingReferenceRepository,
            ExternalInvoiceProviderClient externalInvoiceProviderClient
    ) {
        this.membershipRepository = membershipRepository;
        this.customerRepository = customerRepository;
        this.planRepository = planRepository;
        this.emailService = emailService;
        this.billingSenderEmailAddress = billingSenderEmailAddress;
        this.forFindingCustomers = forFindingCustomers;
        this.forFindingPlans = forFindingPlans;
        this.forStoringMemberships = forStoringMemberships;
        this.forCreatingInvoices = forCreatingInvoices;
        this.forStoringBillingReferences = forStoringBillingReferences;
        this.forSendingEmails = forSendingEmails;
        this.billingReferenceRepository = billingReferenceRepository;
        this.externalInvoiceProviderClient = externalInvoiceProviderClient;
    }

    @Transactional
    @Override
    public ActivateMembershipResult activateMembership(ActivateMembershipInput input) {

        var customer = forFindingCustomers.findCustomerByIdOrThrow(input);

        var plan = planRepository.findById(UUID.fromString(input.planId()))
                .orElseThrow(() -> new PlanNotFoundException(
                        "Plan %s was not found".formatted(input.planId())
                ));

        var startDate = LocalDate.now();
        var endDate = startDate.plusMonths(plan.getDurationInMonths());

        if (Period.between(customer.dateOfBirth(), startDate).getYears() < 18
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
        var externalInvoiceId = externalInvoiceProviderClient.createMembershipInvoice(
                input.customerId(),
                membership,
                plan,
                invoiceDueDate,
                invoiceId
        );
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

        sendEmail(toEmail(billingReference, membership, customer.emailAddress()));

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


    private static @NonNull CustomerActivateMembershipEmail toEmail(MembershipBillingReferenceEntity billingReference, MembershipEntity membership, String emailAddress) {
        return new CustomerActivateMembershipEmail(
                billingReference.getExternalInvoiceReference(),
                billingReference.getDueDate(),
                emailAddress,
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
