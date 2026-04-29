package com.workshop.architecture.fitness.clean_architecture.use_case;

import com.workshop.architecture.fitness.clean_architecture.entity.CustomerActivateMembershipEmail;
import com.workshop.architecture.fitness.clean_architecture.entity.MembershipInvoiceDetails;
import com.workshop.architecture.fitness.clean_architecture.entity.Membership;
import com.workshop.architecture.fitness.clean_architecture.entity.MembershipBillingReference;
import com.workshop.architecture.fitness.clean_architecture.use_case.port.inbound.ActivateMembershipInput;
import com.workshop.architecture.fitness.clean_architecture.use_case.port.inbound.ActivateMembershipResult;
import com.workshop.architecture.fitness.clean_architecture.use_case.port.inbound.ActivateMembershipUseCase;
import com.workshop.architecture.fitness.clean_architecture.use_case.port.outbound.*;
import jakarta.transaction.Transactional;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.UUID;

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

        var membership = Membership.create(customer, planId, input.signedByCustodian(), LocalDate.now(), plan.durationInMonths(), plan.price());
        var storedMembership = forStoringMemberships.storeMembership(membership);

        var invoiceDetails = MembershipInvoiceDetails.create(customerId, membership, plan);
        var externalInvoiceId = forCreatingInvoices.createInvoiceWith(invoiceDetails);
        var billingReference = MembershipBillingReference.create(storedMembership, externalInvoiceId, invoiceDetails);
        var storedBillingReference = forStoringBillingReferences.storeMembershipBillingReference(billingReference);

        var email = CustomerActivateMembershipEmail.toEmail(storedBillingReference, customer.emailAddress(), storedMembership.planPrice());
        forSendingEmails.sendEmail(email);

        return toResult(storedBillingReference, storedMembership);
    }

    private static ActivateMembershipResult toResult(MembershipBillingReference storedBillingReference, Membership membership) {
        return new ActivateMembershipResult(
                storedBillingReference.membershipId().toString(),
                membership.customerId().toString(),
                membership.planId().toString(),
                membership.planPrice(),
                membership.planDurationInMonths(),
                membership.status(),
                membership.startDate(),
                membership.endDate(),
                storedBillingReference.externalInvoiceReference(),
                storedBillingReference.externalInvoiceId(),
                storedBillingReference.dueDate()
        );
    }


}
