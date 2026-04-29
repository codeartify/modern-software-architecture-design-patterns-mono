package com.workshop.architecture.fitness.clean_architecture.adapter.gateway.external;

import com.workshop.architecture.fitness.clean_architecture.use_case.port.outbound.ForCreatingInvoices;
import com.workshop.architecture.fitness.clean_architecture.entity.InvoiceDetails;
import com.workshop.architecture.fitness.layered.infrastructure.external_invoice_provider.ExternalInvoiceProviderClient;
import org.springframework.stereotype.Component;

@Component
public class ExternalInvoiceRepository implements ForCreatingInvoices {

    private final ExternalInvoiceProviderClient externalInvoiceProviderClient;

    public ExternalInvoiceRepository(ExternalInvoiceProviderClient externalInvoiceProviderClient) {
        this.externalInvoiceProviderClient = externalInvoiceProviderClient;
    }

    @Override
    public String createInvoiceWith(InvoiceDetails invoice) {
        return externalInvoiceProviderClient.createMembershipInvoice(
                invoice.customerId().toString(),
                invoice.dueDate(),
                invoice.membershipId().toString(),
                invoice.planTitle(),
                invoice.membershipId(),
                invoice.planPrice().intValue(),
                invoice.planId().toString()
        );
    }
}
