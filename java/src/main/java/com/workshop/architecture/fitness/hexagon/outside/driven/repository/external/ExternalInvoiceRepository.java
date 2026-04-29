package com.workshop.architecture.fitness.hexagon.outside.driven.repository.external;

import com.workshop.architecture.fitness.hexagon.inside.port.outbound.ForCreatingInvoices;
import com.workshop.architecture.fitness.hexagon.inside.port.outbound.InvoiceDetails;
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
