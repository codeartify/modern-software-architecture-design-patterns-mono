package com.workshop.architecture;

import com.workshop.architecture.fitness.layered.infrastructure.CustomerEntity;
import com.workshop.architecture.fitness.layered.infrastructure.CustomerRepository;
import com.workshop.architecture.fitness.layered.presentation.CustomerUpsertRequest;
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

import java.util.UUID;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@TestPropertySource(properties = {
        "spring.datasource.url=jdbc:h2:mem:shared-customer-test;DB_CLOSE_DELAY=-1",
        "spring.jpa.hibernate.ddl-auto=create-drop"
})
class CustomerControllerTest {

    @Autowired
    private WebApplicationContext webApplicationContext;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private CustomerRepository repository;

    private MockMvc mockMvc;

    @BeforeEach
    void setUp() {
        repository.deleteAll();
        mockMvc = MockMvcBuilders.webAppContextSetup(webApplicationContext).build();
    }

    @Test
    void createsReadsUpdatesAndDeletesCustomers() throws Exception {
        String createPayload = objectMapper.writeValueAsString(new CustomerUpsertRequest(
                "Ada Example",
                java.time.LocalDate.parse("1986-08-13"),
                "ada@example.com"
        ));

        String createdJson = mockMvc.perform(post("/api/customers")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(createPayload))
                .andExpect(status().isCreated())
                .andExpect(header().string("Location", org.hamcrest.Matchers.matchesPattern(".*/api/customers/.+")))
                .andExpect(jsonPath("$.name").value("Ada Example"))
                .andExpect(jsonPath("$.dateOfBirth").value("1986-08-13"))
                .andExpect(jsonPath("$.emailAddress").value("ada@example.com"))
                .andReturn()
                .getResponse()
                .getContentAsString();

        UUID customerId = UUID.fromString(objectMapper.readTree(createdJson).get("id").asText());

        mockMvc.perform(get("/api/customers/{customerId}", customerId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(customerId.toString()));

        String updatePayload = objectMapper.writeValueAsString(new CustomerUpsertRequest(
                "Ada Lovelace",
                java.time.LocalDate.parse("1986-08-13"),
                "ada.lovelace@example.com"
        ));

        mockMvc.perform(put("/api/customers/{customerId}", customerId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(updatePayload))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("Ada Lovelace"))
                .andExpect(jsonPath("$.emailAddress").value("ada.lovelace@example.com"));

        mockMvc.perform(get("/api/customers"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(1));

        mockMvc.perform(delete("/api/customers/{customerId}", customerId))
                .andExpect(status().isNoContent());

        mockMvc.perform(get("/api/customers/{customerId}", customerId))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.status").value(404))
                .andExpect(jsonPath("$.error").value("Not Found"))
                .andExpect(jsonPath("$.message").value("Customer %s was not found".formatted(customerId)))
                .andExpect(jsonPath("$.path").value("/api/customers/" + customerId));
    }

    @Test
    void returnsBadRequestForMalformedCustomerId() throws Exception {
        mockMvc.perform(get("/api/customers/not-a-uuid"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.status").value(400))
                .andExpect(jsonPath("$.error").value("Bad Request"))
                .andExpect(jsonPath("$.message").value("Invalid value for 'customerId': not-a-uuid"))
                .andExpect(jsonPath("$.path").value("/api/customers/not-a-uuid"));
    }

    @Test
    void listsCustomersSortedByName() throws Exception {
        repository.save(new CustomerEntity(
                UUID.fromString("22222222-2222-2222-2222-222222222222"),
                "Zoe Zebra",
                java.time.LocalDate.parse("1992-04-21"),
                "zoe@example.com"
        ));
        repository.save(new CustomerEntity(
                UUID.fromString("11111111-1111-1111-1111-111111111111"),
                "Ada Alpha",
                java.time.LocalDate.parse("1986-08-13"),
                "ada@example.com"
        ));

        mockMvc.perform(get("/api/customers"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].name").value("Ada Alpha"))
                .andExpect(jsonPath("$[1].name").value("Zoe Zebra"));
    }
}
