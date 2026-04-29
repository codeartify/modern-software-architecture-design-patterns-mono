package com.workshop.architecture.fitness.clean_architecture.use_case;

import com.workshop.architecture.fitness.clean_architecture.entity.*;
import com.workshop.architecture.fitness.clean_architecture.use_case.exception.CustomerTooYoungException;
import com.workshop.architecture.fitness.clean_architecture.use_case.port.inbound.ActivateMembershipUseCase;
import com.workshop.architecture.fitness.clean_architecture.use_case.port.inbound.ActivateMembershipInput;
import com.workshop.architecture.fitness.clean_architecture.use_case.port.inbound.ActivateMembershipResult;
import com.workshop.architecture.fitness.clean_architecture.use_case.port.outbound.*;
import jakarta.transaction.Transactional;
import org.jspecify.annotations.NonNull;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;

import static java.lang.Boolean.TRUE;

@Service
public class ActivateMembershipUseCaseInteractor implements ActivateMembershipUseCase {
    private final ForFindingCustomers forFindingCustomers;
    private final ForFindingPlans forFindingPlans;
    private final ForStoringMemberships forStoringMemberships;
    private final ForCreatingInvoices forCreatingInvoices;
    private final ForStoringBillingReferences forStoringBillingReferences;
    private final ForSendingEmails forSendingEmails;

    public ActivateMembershipUseCaseInteractor(
            ForFindingCustomers forFindingCustomers,
            ForFindingPlans forFindingPlans,
            ForStoringMemberships forStoringMemberships,
            ForCreatingInvoices forCreatingInvoices,
            ForStoringBillingReferences forStoringBillingReferences,
            ForSendingEmails forSendingEmails
    ) {
        this.forFindingCustomers = forFindingCustomers;
        this.forFindingPlans = forFindingPlans;
        this.forStoringMemberships = forStoringMemberships;
        this.forCreatingInvoices = forCreatingInvoices;
        this.forStoringBillingReferences = forStoringBillingReferences;
        this.forSendingEmails = forSendingEmails;
    }

    @Transactional
    @Override
    public ActivateMembershipResult activateMembership(ActivateMembershipInput input) {

        var customerId = UUID.fromString(input.customerId());
        var customer = forFindingCustomers.findCustomerById(customerId);

        var planId = UUID.fromString(input.planId());
        var plan = forFindingPlans.findPlanById(planId);

        var membership = createMembership(customer, customerId, planId, input.signedByCustodian(), LocalDate.now(), plan.durationInMonths(), plan.price());

        var storedMembership = forStoringMemberships.storeMembership(membership);
        var invoiceDetails = new InvoiceDetails(
                UUID.randomUUID(),
                customerId,
                membership.id(),
                plan.id(),
                LocalDate.now().plusDays(30),
                plan.title(),
                plan.price());

        var externalInvoiceId = forCreatingInvoices.createInvoiceWith(invoiceDetails);


        var now = Instant.now();
        var billingReference = new MembershipBillingReference(
                UUID.randomUUID(),
                storedMembership.id(),
                externalInvoiceId,
                invoiceDetails.membershipId().toString(),
                invoiceDetails.dueDate(),
                "OPEN",
                now,
                now
        );

        var storedBillingReference = forStoringBillingReferences.storeMembershipBillingReference(billingReference);

        forSendingEmails.sendEmail(toEmail(storedBillingReference, customer.emailAddress(), storedMembership.planPrice()));

        return new ActivateMembershipResult(
                storedBillingReference.membershipId().toString(),
                storedMembership.customerId().toString(),
                storedMembership.planId().toString(),
                storedMembership.planPrice(),
                storedMembership.planDurationInMonths(),
                storedMembership.status(),
                storedMembership.startDate(),
                storedMembership.endDate(),
                storedBillingReference.externalInvoiceReference(),
                storedBillingReference.externalInvoiceId(),
                storedBillingReference.dueDate()
        );
    }

    private static Membership createMembership(Customer customer, UUID customerId, UUID planId, Boolean isSignedByCustodian, LocalDate startDate, int planDurationInMonths, BigDecimal planPrice) {
        var endDate = startDate.plusMonths(planDurationInMonths);

        if (!customer.isAdultAt(startDate) && isMissingSignature(isSignedByCustodian)) {
            throw new CustomerTooYoungException(
                    "Customers younger than 18 require signedByCustodian=true"
            );
        }

        return new Membership(
                UUID.randomUUID(),
                customerId,
                planId,
                planPrice.intValue(),
                planDurationInMonths,
                "ACTIVE",
                null,
                startDate,
                endDate
        );
    }

    private static boolean isMissingSignature(Boolean isSignedByCustodian) {
        return !TRUE.equals(isSignedByCustodian);
    }


    private static @NonNull CustomerActivateMembershipEmail toEmail(MembershipBillingReference billingReference, String emailAddress, int membershipPlanPrice) {
        return new CustomerActivateMembershipEmail(
                billingReference.externalInvoiceReference(),
                billingReference.dueDate(),
                emailAddress,
                membershipPlanPrice,
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

}
