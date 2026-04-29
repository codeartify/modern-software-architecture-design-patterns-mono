package com.workshop.architecture.fitness.clean_architecture.adapter.gateway.external;

import com.workshop.architecture.fitness.clean_architecture.entity.MembershipInvoiceDetails;
import com.workshop.architecture.fitness.clean_architecture.use_case.port.outbound.ForCreatingInvoices;
import com.workshop.architecture.fitness.layered.infrastructure.external_invoice_provider.ExternalInvoiceProviderResponse;
import com.workshop.architecture.fitness.layered.infrastructure.external_invoice_provider.ExternalInvoiceProviderStatus;
import com.workshop.architecture.fitness.layered.infrastructure.external_invoice_provider.ExternalInvoiceProviderUpsertRequest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.Map;

@Component
public class ExternalInvoiceProviderClient implements ForCreatingInvoices {

    private final RestClient restClient;

    public ExternalInvoiceProviderClient(
            RestClient.Builder restClientBuilder,
            @Value("${workshop.external-invoice-provider.base-url}") String baseUrl
    ) {
        this.restClient = restClientBuilder
                .baseUrl(baseUrl)
                .build();
    }


    @Override
    public String createInvoiceWith(MembershipInvoiceDetails invoice) {
        var request = new ExternalInvoiceProviderUpsertRequest(
                invoice.customerId().toString(),
                invoice.membershipId().toString(),
                invoice.planPrice().intValue(),
                "CHF",
                invoice.dueDate(),
                ExternalInvoiceProviderStatus.OPEN,
                "Membership invoice for %s".formatted(invoice.planTitle()),
                invoice.membershipId().toString(),
                Map.of(
                        "exercise", "membership",
                        "planId", invoice.planId().toString()
                )
        );

        var externalInvoice = restClient.post()
                .uri("/api/shared/external-invoice-provider/invoices")
                .contentType(MediaType.APPLICATION_JSON)
                .body(request)
                .retrieve()
                .body(ExternalInvoiceProviderResponse.class);

        return externalInvoice == null
                ? invoice.membershipId().toString()
                : externalInvoice.invoiceId();
    }

}
