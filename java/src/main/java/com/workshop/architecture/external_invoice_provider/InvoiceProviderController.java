package com.workshop.architecture.external_invoice_provider;

import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;
import org.springframework.web.server.ResponseStatusException;

import java.net.URI;
import java.time.Instant;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/shared/external-invoice-provider/invoices")
public class InvoiceProviderController {

    private final InvoiceProviderStore store;
    private final RestClient restClient;

    public InvoiceProviderController(
            InvoiceProviderStore store,
            RestClient.Builder restClientBuilder,
            @Value("${workshop.fitness-api.base-url}") String fitnessApiBaseUrl
    ) {
        this.store = store;
        this.restClient = restClientBuilder.baseUrl(fitnessApiBaseUrl).build();
    }

    @GetMapping
    List<InvoiceProviderResponse> listInvoices() {
        return store.findAll();
    }

    @GetMapping("/{invoiceId}")
    InvoiceProviderResponse getInvoice(@PathVariable String invoiceId) {
        return store.findById(invoiceId)
                .orElseThrow(() -> notFound(invoiceId));
    }

    @PostMapping
    ResponseEntity<InvoiceProviderResponse> createInvoice(
            @Valid @RequestBody InvoiceProviderUpsertRequest request
    ) {
        String invoiceId = UUID.randomUUID().toString();
        InvoiceProviderResponse response = store.save(invoiceId, request);
        return ResponseEntity
                .created(URI.create("/api/shared/external-invoice-provider/invoices/" + invoiceId))
                .body(response);
    }

    @PostMapping("/{invoiceId}/mark-paid")
    InvoiceProviderResponse markInvoicePaid(@PathVariable String invoiceId) {
        InvoiceProviderResponse invoice = store.findById(invoiceId)
                .orElseThrow(() -> notFound(invoiceId));

        if (invoice.status() == InvoiceProviderStatus.PAID) {
            return invoice;
        }

        InvoiceProviderResponse paidInvoice = store.save(new InvoiceProviderResponse(
                invoice.invoiceId(),
                invoice.customerReference(),
                invoice.contractReference(),
                invoice.amountInCents(),
                invoice.currency(),
                invoice.dueDate(),
                InvoiceProviderStatus.PAID,
                invoice.description(),
                invoice.externalCorrelationId(),
                invoice.metadata()
        ));

        try {
            restClient.post()
                    .uri("/api/memberships/payment-received")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(new InvoiceProviderPaymentReceivedCallbackRequest(
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
    InvoiceProviderResponse updateInvoice(
            @PathVariable String invoiceId,
            @Valid @RequestBody InvoiceProviderUpsertRequest request
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
