package com.workshop.architecture.fitness.layered.infrastructure.external_invoice_provider;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.time.LocalDate;
import java.util.Map;
import java.util.UUID;

@Component
public class ExternalInvoiceProviderClient {

    private final RestClient restClient;

    public ExternalInvoiceProviderClient(
            RestClient.Builder restClientBuilder,
            @Value("${workshop.external-invoice-provider.base-url}") String baseUrl
    ) {
        this.restClient = restClientBuilder
                .baseUrl(baseUrl)
                .build();
    }

    public String createMembershipInvoice(
            String customerId,
            LocalDate invoiceDueDate,
            String invoiceId,
            String planTitle,
            UUID membershipId,
            int membershipPlanPrice,
            String membershipPlanId
    ) {
        var request = new ExternalInvoiceProviderUpsertRequest(
                customerId,
                membershipId.toString(),
                membershipPlanPrice,
                "CHF",
                invoiceDueDate,
                ExternalInvoiceProviderStatus.OPEN,
                "Membership invoice for %s".formatted(planTitle),
                invoiceId,
                Map.of(
                        "exercise", "membership",
                        "planId", membershipPlanId
                )
        );

        var externalInvoice = restClient.post()
                .uri("/api/shared/external-invoice-provider/invoices")
                .contentType(MediaType.APPLICATION_JSON)
                .body(request)
                .retrieve()
                .body(ExternalInvoiceProviderResponse.class);

        return externalInvoice == null
                ? invoiceId
                : externalInvoice.invoiceId();
    }
}
