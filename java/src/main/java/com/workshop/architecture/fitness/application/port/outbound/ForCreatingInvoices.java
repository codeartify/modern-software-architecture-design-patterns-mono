package com.workshop.architecture.fitness.application.port.outbound;

import com.workshop.architecture.fitness.domain.InvoiceDetails;

public interface ForCreatingInvoices {
    String createInvoiceWith(InvoiceDetails invoiceDetails);
}
