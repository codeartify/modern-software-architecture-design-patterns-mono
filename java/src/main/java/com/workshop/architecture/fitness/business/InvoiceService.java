package com.workshop.architecture.fitness.business;

import com.workshop.architecture.fitness.infrastructure.external_invoice_provider.ExternalInvoiceProviderResponse;
import com.workshop.architecture.fitness.infrastructure.external_invoice_provider.ExternalInvoiceProviderStatus;
import com.workshop.architecture.fitness.infrastructure.external_invoice_provider.ExternalInvoiceProviderUpsertRequest;
import com.workshop.architecture.fitness.infrastructure.MembershipBillingReferenceEntity;
import com.workshop.architecture.fitness.infrastructure.MembershipBillingReferenceRepository;
import com.workshop.architecture.fitness.infrastructure.MembershipEntity;
import com.workshop.architecture.fitness.infrastructure.PlanEntity;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.time.Instant;
import java.time.LocalDate;
import java.util.Map;
import java.util.UUID;

@Service
public class InvoiceService {
    private final MembershipBillingReferenceRepository billingReferenceRepository;
    private final RestClient restClient;

    public InvoiceService(
            MembershipBillingReferenceRepository billingReferenceRepository,
            RestClient.Builder restClientBuilder,
            @Value("${workshop.external-invoice-provider.base-url}") String externalInvoiceProviderBaseUrl
    ) {
        this.billingReferenceRepository = billingReferenceRepository;
        this.restClient = restClientBuilder.baseUrl(externalInvoiceProviderBaseUrl).build();
    }

    public MembershipBillingReferenceEntity createInvoice(String customerId, MembershipEntity membership, PlanEntity plan) {

        var invoiceId = UUID.randomUUID().toString();
        var invoiceDueDate = LocalDate.now().plusDays(30);
        var now = Instant.now();

        var externalInvoice = restClient.post()
                .uri("/api/shared/external-invoice-provider/invoices")
                .contentType(MediaType.APPLICATION_JSON)
                .body(new ExternalInvoiceProviderUpsertRequest(
                        customerId,
                        membership.getId().toString(),
                        membership.getPlanPrice(),
                        "CHF",
                        invoiceDueDate,
                        ExternalInvoiceProviderStatus.OPEN,
                        "Membership invoice for %s".formatted(plan.getTitle()),
                        invoiceId,
                        Map.of(
                                "exercise", "membership",
                                "planId", membership.getPlanId()
                        )
                ))
                .retrieve()
                .body(ExternalInvoiceProviderResponse.class);

        var externalInvoiceId = externalInvoice == null ? invoiceId : externalInvoice.invoiceId();

        var billingReference = new MembershipBillingReferenceEntity(
                UUID.randomUUID(),
                membership.getId(),
                externalInvoiceId,
                invoiceId,
                invoiceDueDate,
                "OPEN",
                now,
                now
        );

        return billingReferenceRepository.save(billingReference);
    }

}
