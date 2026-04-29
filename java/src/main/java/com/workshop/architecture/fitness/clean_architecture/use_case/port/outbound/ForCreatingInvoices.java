package com.workshop.architecture.fitness.clean_architecture.use_case.port.outbound;

import com.workshop.architecture.fitness.clean_architecture.entity.InvoiceDetails;

public interface ForCreatingInvoices {
    String createInvoiceWith(InvoiceDetails invoiceDetails);
}
