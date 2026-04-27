package com.workshop.architecture.fitness.external_invoice_provider;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.time.LocalDate;
import java.util.Map;

import com.workshop.architecture.fitness.external_invoice_provider.ExternalInvoiceProviderStatus;
import com.workshop.architecture.fitness.external_invoice_provider.ExternalInvoiceProviderStore;
import com.workshop.architecture.fitness.external_invoice_provider.ExternalInvoiceProviderUpsertRequest;
import org.hamcrest.Matchers;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;
import tools.jackson.databind.ObjectMapper;

@SpringBootTest
class ExternalInvoiceProviderControllerTest {

    @Autowired
    private WebApplicationContext webApplicationContext;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private ExternalInvoiceProviderStore store;

    private MockMvc mockMvc;

    @BeforeEach
    void setUp() {
        store.clear();
        mockMvc = MockMvcBuilders.webAppContextSetup(webApplicationContext).build();
    }

    @Test
    void createsReadsUpdatesAndDeletesExternalInvoices() throws Exception {
        String createPayload = objectMapper.writeValueAsString(new ExternalInvoiceProviderUpsertRequest(
                "customer-adult-1",
                "membership-001",
                99900,
                "CHF",
                LocalDate.parse("2026-05-27"),
                ExternalInvoiceProviderStatus.OPEN,
                "Annual membership invoice",
                "activation-123",
                Map.of("origin", "fitness-system")
        ));

        String createdJson = mockMvc.perform(post("/api/shared/external-invoice-provider/invoices")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(createPayload))
                .andExpect(status().isCreated())
                .andExpect(header().string(
                        "Location",
                        Matchers.matchesPattern(".*/api/shared/external-invoice-provider/invoices/.+")
                ))
                .andExpect(jsonPath("$.customerReference").value("customer-adult-1"))
                .andExpect(jsonPath("$.contractReference").value("membership-001"))
                .andExpect(jsonPath("$.amountInCents").value(99900))
                .andReturn()
                .getResponse()
                .getContentAsString();

        String invoiceId = objectMapper.readTree(createdJson).get("invoiceId").asText();

        mockMvc.perform(get("/api/shared/external-invoice-provider/invoices/{invoiceId}", invoiceId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.invoiceId").value(invoiceId));

        String updatePayload = objectMapper.writeValueAsString(new ExternalInvoiceProviderUpsertRequest(
                "customer-adult-1",
                "membership-001",
                99900,
                "CHF",
                LocalDate.parse("2026-05-27"),
                ExternalInvoiceProviderStatus.PAID,
                "Annual membership invoice paid",
                "payment-456",
                Map.of("origin", "fitness-system", "paymentReference", "pay-123")
        ));

        mockMvc.perform(put("/api/shared/external-invoice-provider/invoices/{invoiceId}", invoiceId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(updatePayload))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("PAID"))
                .andExpect(jsonPath("$.externalCorrelationId").value("payment-456"));

        mockMvc.perform(get("/api/shared/external-invoice-provider/invoices"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(1));

        mockMvc.perform(delete("/api/shared/external-invoice-provider/invoices/{invoiceId}", invoiceId))
                .andExpect(status().isNoContent());

        mockMvc.perform(get("/api/shared/external-invoice-provider/invoices/{invoiceId}", invoiceId))
                .andExpect(status().isNotFound());
    }
}
