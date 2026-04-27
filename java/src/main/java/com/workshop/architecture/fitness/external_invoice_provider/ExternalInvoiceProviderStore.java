package com.workshop.architecture.fitness.external_invoice_provider;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.springframework.stereotype.Component;

@Component
public class ExternalInvoiceProviderStore {

    private final Map<String, ExternalInvoiceProviderResponse> invoices = new LinkedHashMap<>();

    public List<ExternalInvoiceProviderResponse> findAll() {
        return new ArrayList<>(invoices.values());
    }

    public Optional<ExternalInvoiceProviderResponse> findById(String invoiceId) {
        return Optional.ofNullable(invoices.get(invoiceId));
    }

    public ExternalInvoiceProviderResponse save(String invoiceId, ExternalInvoiceProviderUpsertRequest request) {
        ExternalInvoiceProviderResponse response = new ExternalInvoiceProviderResponse(
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

    public void delete(String invoiceId) {
        invoices.remove(invoiceId);
    }

    public void clear() {
        invoices.clear();
    }
}
