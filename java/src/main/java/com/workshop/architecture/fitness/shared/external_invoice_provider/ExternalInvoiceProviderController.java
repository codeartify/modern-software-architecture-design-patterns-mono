package com.workshop.architecture.fitness.shared.external_invoice_provider;

import jakarta.validation.Valid;
import java.net.URI;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/shared/external-invoice-provider/invoices")
public class ExternalInvoiceProviderController {

    private final ExternalInvoiceProviderStore store;

    public ExternalInvoiceProviderController(ExternalInvoiceProviderStore store) {
        this.store = store;
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
