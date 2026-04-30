package com.workshop.architecture.external_invoice_provider;

import org.springframework.stereotype.Component;

import java.util.*;

@Component
public class InvoiceProviderStore {

    private final Map<String, InvoiceProviderResponse> invoices = new LinkedHashMap<>();

    public List<InvoiceProviderResponse> findAll() {
        return new ArrayList<>(invoices.values());
    }

    public Optional<InvoiceProviderResponse> findById(String invoiceId) {
        return Optional.ofNullable(invoices.get(invoiceId));
    }

    public InvoiceProviderResponse save(String invoiceId, InvoiceProviderUpsertRequest request) {
        InvoiceProviderResponse response = new InvoiceProviderResponse(
                invoiceId,
                request.customerReference(),
                request.contractReference(),
                request.amountInCents(),
                request.currency(),
                request.dueDate(),
                request.status(),
                request.description(),
                request.externalCorrelationId(),
                request.metadata()
        );
        invoices.put(invoiceId, response);
        return response;
    }

    public InvoiceProviderResponse save(InvoiceProviderResponse response) {
        invoices.put(response.invoiceId(), response);
        return response;
    }

    public void delete(String invoiceId) {
        invoices.remove(invoiceId);
    }

    public void clear() {
        invoices.clear();
    }
}
