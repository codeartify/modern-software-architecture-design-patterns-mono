package com.workshop.architecture.fitness.infrastructure.external_invoice_provider;

import com.workshop.architecture.fitness.infrastructure.MembershipEntity;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.time.LocalDate;
import java.util.Map;

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
            MembershipEntity membership,
            LocalDate invoiceDueDate,
            String invoiceId,
            String planTitle
    ) {
        var request = new ExternalInvoiceProviderUpsertRequest(
                customerId,
                membership.getId().toString(),
                membership.getPlanPrice(),
                "CHF",
                invoiceDueDate,
                ExternalInvoiceProviderStatus.OPEN,
                "Membership invoice for %s".formatted(planTitle),
                invoiceId,
                Map.of(
                        "exercise", "membership",
                        "planId", membership.getPlanId()
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
