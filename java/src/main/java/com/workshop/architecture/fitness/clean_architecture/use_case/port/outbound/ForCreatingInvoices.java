package com.workshop.architecture.fitness.clean_architecture.use_case.port.outbound;

import com.workshop.architecture.fitness.clean_architecture.entity.MembershipInvoiceDetails;

public interface ForCreatingInvoices {
    String createInvoiceWith(MembershipInvoiceDetails membershipInvoiceDetails);
}
