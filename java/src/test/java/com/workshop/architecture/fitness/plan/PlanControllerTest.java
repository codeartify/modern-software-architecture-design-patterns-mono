package com.workshop.architecture.fitness.plan;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.math.BigDecimal;
import java.util.UUID;
import org.hamcrest.Matchers;
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
        "spring.datasource.url=jdbc:h2:mem:shared-plan-test;DB_CLOSE_DELAY=-1",
        "spring.jpa.hibernate.ddl-auto=create-drop"
})
class PlanControllerTest {

    @Autowired
    private WebApplicationContext webApplicationContext;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private PlanRepository repository;

    private MockMvc mockMvc;

    @BeforeEach
    void setUp() {
        repository.deleteAll();
        mockMvc = MockMvcBuilders.webAppContextSetup(webApplicationContext).build();
    }

    @Test
    void createsReadsUpdatesAndDeletesPlans() throws Exception {
        String createPayload = objectMapper.writeValueAsString(new PlanUpsertRequest(
                "Premium 12 Months",
                "Twelve months for regular training",
                12,
                new BigDecimal("999.00")
        ));

        String createdJson = mockMvc.perform(post("/api/plans")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(createPayload))
                .andExpect(status().isCreated())
                .andExpect(header().string("Location", Matchers.matchesPattern(".*/api/plans/.+")))
                .andExpect(jsonPath("$.title").value("Premium 12 Months"))
                .andExpect(jsonPath("$.durationInMonths").value(12))
                .andExpect(jsonPath("$.price").value(999.00))
                .andReturn()
                .getResponse()
                .getContentAsString();

        UUID planId = UUID.fromString(objectMapper.readTree(createdJson).get("id").asText());

        mockMvc.perform(get("/api/plans/{planId}", planId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(planId.toString()));

        String updatePayload = objectMapper.writeValueAsString(new PlanUpsertRequest(
                "Premium 24 Months",
                "Twenty-four months for long-term training",
                24,
                new BigDecimal("1699.00")
        ));

        mockMvc.perform(put("/api/plans/{planId}", planId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(updatePayload))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.title").value("Premium 24 Months"))
                .andExpect(jsonPath("$.durationInMonths").value(24))
                .andExpect(jsonPath("$.price").value(1699.00));

        mockMvc.perform(get("/api/plans"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(1));

        mockMvc.perform(delete("/api/plans/{planId}", planId))
                .andExpect(status().isNoContent());

        mockMvc.perform(get("/api/plans/{planId}", planId))
                .andExpect(status().isNotFound());
    }

    @Test
    void listsPlansSortedByTitle() throws Exception {
        repository.save(new PlanEntity(
                UUID.fromString("22222222-2222-2222-2222-222222222222"),
                "Zeta Plan",
                "Late alphabet plan",
                12,
                new BigDecimal("999.00")
        ));
        repository.save(new PlanEntity(
                UUID.fromString("11111111-1111-1111-1111-111111111111"),
                "Alpha Plan",
                "Early alphabet plan",
                1,
                new BigDecimal("129.00")
        ));

        mockMvc.perform(get("/api/plans"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].title").value("Alpha Plan"))
                .andExpect(jsonPath("$[1].title").value("Zeta Plan"));
    }
}
