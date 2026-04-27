package com.workshop.architecture.fitness.customer;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.util.UUID;

import com.workshop.architecture.fitness.customer.SharedCustomerRepository;
import com.workshop.architecture.fitness.customer.SharedCustomerUpsertRequest;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;
import tools.jackson.databind.ObjectMapper;

@SpringBootTest
@TestPropertySource(properties = {
        "spring.datasource.url=jdbc:h2:mem:shared-customer-test;DB_CLOSE_DELAY=-1",
        "spring.jpa.hibernate.ddl-auto=create-drop"
})
class SharedCustomerControllerTest {

    @Autowired
    private WebApplicationContext webApplicationContext;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private SharedCustomerRepository repository;

    private MockMvc mockMvc;

    @BeforeEach
    void setUp() {
        repository.deleteAll();
        mockMvc = MockMvcBuilders.webAppContextSetup(webApplicationContext).build();
    }

    @Test
    void createsReadsUpdatesAndDeletesCustomers() throws Exception {
        String createPayload = objectMapper.writeValueAsString(new SharedCustomerUpsertRequest(
                "Ada Example",
                java.time.LocalDate.parse("1986-08-13"),
                "ada@example.com"
        ));

        String createdJson = mockMvc.perform(post("/api/shared/customers")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(createPayload))
                .andExpect(status().isCreated())
                .andExpect(header().string("Location", org.hamcrest.Matchers.matchesPattern(".*/api/shared/customers/.+")))
                .andExpect(jsonPath("$.name").value("Ada Example"))
                .andExpect(jsonPath("$.dateOfBirth").value("1986-08-13"))
                .andExpect(jsonPath("$.emailAddress").value("ada@example.com"))
                .andReturn()
                .getResponse()
                .getContentAsString();

        UUID customerId = UUID.fromString(objectMapper.readTree(createdJson).get("id").asText());

        mockMvc.perform(get("/api/shared/customers/{customerId}", customerId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(customerId.toString()));

        String updatePayload = objectMapper.writeValueAsString(new SharedCustomerUpsertRequest(
                "Ada Lovelace",
                java.time.LocalDate.parse("1986-08-13"),
                "ada.lovelace@example.com"
        ));

        mockMvc.perform(put("/api/shared/customers/{customerId}", customerId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(updatePayload))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("Ada Lovelace"))
                .andExpect(jsonPath("$.emailAddress").value("ada.lovelace@example.com"));

        mockMvc.perform(get("/api/shared/customers"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(1));

        mockMvc.perform(delete("/api/shared/customers/{customerId}", customerId))
                .andExpect(status().isNoContent());

        mockMvc.perform(get("/api/shared/customers/{customerId}", customerId))
                .andExpect(status().isNotFound());
    }
}
