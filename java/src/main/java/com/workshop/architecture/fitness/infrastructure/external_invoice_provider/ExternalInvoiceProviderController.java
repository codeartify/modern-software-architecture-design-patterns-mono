package com.workshop.architecture.fitness.infrastructure.external_invoice_provider;

import jakarta.validation.Valid;
import java.net.URI;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/shared/external-invoice-provider/invoices")
public class ExternalInvoiceProviderController {

    private final ExternalInvoiceProviderStore store;
    private final RestClient restClient;

    public ExternalInvoiceProviderController(
            ExternalInvoiceProviderStore store,
            RestClient.Builder restClientBuilder,
            @Value("${workshop.fitness-api.base-url}") String fitnessApiBaseUrl
    ) {
        this.store = store;
        this.restClient = restClientBuilder.baseUrl(fitnessApiBaseUrl).build();
    }

    @GetMapping
    List<ExternalInvoiceProviderResponse> listInvoices() {
        return store.findAll();
    }

    @GetMapping("/{invoiceId}")
    ExternalInvoiceProviderResponse getInvoice(@PathVariable String invoiceId) {
        return store.findById(invoiceId)
                .orElseThrow(() -> notFound(invoiceId));
    }

    @PostMapping
    ResponseEntity<ExternalInvoiceProviderResponse> createInvoice(
            @Valid @RequestBody ExternalInvoiceProviderUpsertRequest request
    ) {
        String invoiceId = UUID.randomUUID().toString();
        ExternalInvoiceProviderResponse response = store.save(invoiceId, request);
        return ResponseEntity
                .created(URI.create("/api/shared/external-invoice-provider/invoices/" + invoiceId))
                .body(response);
    }

    @PostMapping("/{invoiceId}/mark-paid")
    ExternalInvoiceProviderResponse markInvoicePaid(@PathVariable String invoiceId) {
        ExternalInvoiceProviderResponse invoice = store.findById(invoiceId)
                .orElseThrow(() -> notFound(invoiceId));

        if (invoice.status() == ExternalInvoiceProviderStatus.PAID) {
            return invoice;
        }

        ExternalInvoiceProviderResponse paidInvoice = store.save(new ExternalInvoiceProviderResponse(
                invoice.invoiceId(),
                invoice.customerReference(),
                invoice.contractReference(),
                invoice.amountInCents(),
                invoice.currency(),
                invoice.dueDate(),
                ExternalInvoiceProviderStatus.PAID,
                invoice.description(),
                invoice.externalCorrelationId(),
                invoice.metadata()
        ));

        try {
            restClient.post()
                    .uri("/api/memberships/payment-received")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(new ExternalInvoiceProviderPaymentReceivedCallbackRequest(
                            paidInvoice.invoiceId(),
                            paidInvoice.externalCorrelationId(),
                            paidInvoice.contractReference(),
                            Instant.now()
                    ))
                    .retrieve()
                    .toBodilessEntity();
        } catch (RestClientException ignored) {
            // Step 2 keeps payment simulation usable even if the callback receiver is not live yet.
        }

        return paidInvoice;
    }

    @PutMapping("/{invoiceId}")
    ExternalInvoiceProviderResponse updateInvoice(
            @PathVariable String invoiceId,
            @Valid @RequestBody ExternalInvoiceProviderUpsertRequest request
    ) {
        if (store.findById(invoiceId).isEmpty()) {
            throw notFound(invoiceId);
        }
        return store.save(invoiceId, request);
    }

    @DeleteMapping("/{invoiceId}")
    ResponseEntity<Void> deleteInvoice(@PathVariable String invoiceId) {
        if (store.findById(invoiceId).isEmpty()) {
            throw notFound(invoiceId);
        }
        store.delete(invoiceId);
        return ResponseEntity.noContent().build();
    }

    private ResponseStatusException notFound(String invoiceId) {
        return new ResponseStatusException(
                HttpStatus.NOT_FOUND,
                "External invoice %s was not found".formatted(invoiceId)
        );
    }
}
