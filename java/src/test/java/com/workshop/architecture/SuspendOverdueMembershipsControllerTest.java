package com.workshop.architecture;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;

import com.workshop.architecture.fitness.MembershipBillingReferenceEntity;
import com.workshop.architecture.fitness.MembershipBillingReferenceRepository;
import com.workshop.architecture.fitness.MembershipEntity;
import com.workshop.architecture.fitness.MembershipRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;

@SpringBootTest
class SuspendOverdueMembershipsControllerTest {

    @DynamicPropertySource
    static void registerProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", () -> "jdbc:h2:mem:membership-suspend-overdue-test;DB_CLOSE_DELAY=-1");
        registry.add("spring.jpa.hibernate.ddl-auto", () -> "create-drop");
    }

    @Autowired
    private WebApplicationContext webApplicationContext;

    @Autowired
    private MembershipRepository membershipRepository;

    @Autowired
    private MembershipBillingReferenceRepository billingReferenceRepository;

    private MockMvc mockMvc;

    @BeforeEach
    void setUp() {
        billingReferenceRepository.deleteAll();
        membershipRepository.deleteAll();
        mockMvc = MockMvcBuilders.webAppContextSetup(webApplicationContext).build();
    }

    @Test
    void suspendOverdueUsesOpenBillingReferencesAndIgnoresPaidFutureSuspendedAndCancelledMemberships()
            throws Exception {
        MembershipEntity activeOverdueMembership = membershipRepository.save(new MembershipEntity(
                UUID.randomUUID(),
                "11111111-1111-1111-1111-111111111111",
                "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                999,
                12,
                "ACTIVE",
                null,
                LocalDate.parse("2026-01-01"),
                LocalDate.parse("2027-01-01")
        ));
        MembershipEntity activePaidMembership = membershipRepository.save(new MembershipEntity(
                UUID.randomUUID(),
                "11111111-1111-1111-1111-111111111111",
                "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                999,
                12,
                "ACTIVE",
                null,
                LocalDate.parse("2026-01-01"),
                LocalDate.parse("2027-01-01")
        ));
        MembershipEntity activeFutureMembership = membershipRepository.save(new MembershipEntity(
                UUID.randomUUID(),
                "11111111-1111-1111-1111-111111111111",
                "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                999,
                12,
                "ACTIVE",
                null,
                LocalDate.parse("2026-01-01"),
                LocalDate.parse("2027-01-01")
        ));
        MembershipEntity suspendedMembership = membershipRepository.save(new MembershipEntity(
                UUID.randomUUID(),
                "11111111-1111-1111-1111-111111111111",
                "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                999,
                12,
                "SUSPENDED",
                "NON_PAYMENT",
                LocalDate.parse("2026-01-01"),
                LocalDate.parse("2027-01-01")
        ));
        MembershipEntity cancelledMembership = membershipRepository.save(new MembershipEntity(
                UUID.randomUUID(),
                "11111111-1111-1111-1111-111111111111",
                "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                999,
                12,
                "CANCELLED",
                null,
                LocalDate.parse("2026-01-01"),
                LocalDate.parse("2027-01-01")
        ));

        billingReferenceRepository.save(new MembershipBillingReferenceEntity(
                UUID.randomUUID(),
                activeOverdueMembership.getId(),
                "external-open-overdue",
                "local-open-overdue",
                LocalDate.parse("2026-04-01"),
                "OPEN",
                Instant.parse("2026-01-01T10:00:00Z"),
                Instant.parse("2026-01-01T10:00:00Z")
        ));
        billingReferenceRepository.save(new MembershipBillingReferenceEntity(
                UUID.randomUUID(),
                activePaidMembership.getId(),
                "external-paid",
                "local-paid",
                LocalDate.parse("2026-04-01"),
                "PAID",
                Instant.parse("2026-01-01T10:00:00Z"),
                Instant.parse("2026-01-01T10:00:00Z")
        ));
        billingReferenceRepository.save(new MembershipBillingReferenceEntity(
                UUID.randomUUID(),
                activeFutureMembership.getId(),
                "external-future",
                "local-future",
                LocalDate.parse("2026-05-10"),
                "OPEN",
                Instant.parse("2026-01-01T10:00:00Z"),
                Instant.parse("2026-01-01T10:00:00Z")
        ));
        billingReferenceRepository.save(new MembershipBillingReferenceEntity(
                UUID.randomUUID(),
                suspendedMembership.getId(),
                "external-suspended",
                "local-suspended",
                LocalDate.parse("2026-04-01"),
                "OPEN",
                Instant.parse("2026-01-01T10:00:00Z"),
                Instant.parse("2026-01-01T10:00:00Z")
        ));
        billingReferenceRepository.save(new MembershipBillingReferenceEntity(
                UUID.randomUUID(),
                cancelledMembership.getId(),
                "external-cancelled",
                "local-cancelled",
                LocalDate.parse("2026-04-01"),
                "OPEN",
                Instant.parse("2026-01-01T10:00:00Z"),
                Instant.parse("2026-01-01T10:00:00Z")
        ));

        mockMvc.perform(post("/api/memberships/suspend-overdue")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "checkedAt": "2026-04-28T10:00:00Z"
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.checkedMemberships").value(3))
                .andExpect(jsonPath("$.suspendedMembershipIds.length()").value(1))
                .andExpect(jsonPath("$.suspendedMembershipIds[0]").value(activeOverdueMembership.getId().toString()));

        assertThat(membershipRepository.findById(activeOverdueMembership.getId()).orElseThrow().getStatus())
                .isEqualTo("SUSPENDED");
        assertThat(membershipRepository.findById(activeOverdueMembership.getId()).orElseThrow().getReason())
                .isEqualTo("NON_PAYMENT");
        assertThat(membershipRepository.findById(activePaidMembership.getId()).orElseThrow().getStatus())
                .isEqualTo("ACTIVE");
        assertThat(membershipRepository.findById(activeFutureMembership.getId()).orElseThrow().getStatus())
                .isEqualTo("ACTIVE");
        assertThat(membershipRepository.findById(suspendedMembership.getId()).orElseThrow().getStatus())
                .isEqualTo("SUSPENDED");
        assertThat(membershipRepository.findById(cancelledMembership.getId()).orElseThrow().getStatus())
                .isEqualTo("CANCELLED");
    }

    @Test
    void suspendOverdueIsIdempotent() throws Exception {
        MembershipEntity activeOverdueMembership = membershipRepository.save(new MembershipEntity(
                UUID.randomUUID(),
                "11111111-1111-1111-1111-111111111111",
                "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                999,
                12,
                "ACTIVE",
                null,
                LocalDate.parse("2026-01-01"),
                LocalDate.parse("2027-01-01")
        ));

        billingReferenceRepository.save(new MembershipBillingReferenceEntity(
                UUID.randomUUID(),
                activeOverdueMembership.getId(),
                "external-open-overdue",
                "local-open-overdue",
                LocalDate.parse("2026-04-01"),
                "OPEN",
                Instant.parse("2026-01-01T10:00:00Z"),
                Instant.parse("2026-01-01T10:00:00Z")
        ));

        mockMvc.perform(post("/api/memberships/suspend-overdue")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "checkedAt": "2026-04-28T10:00:00Z"
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.suspendedMembershipIds.length()").value(1));

        mockMvc.perform(post("/api/memberships/suspend-overdue")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "checkedAt": "2026-04-28T10:00:00Z"
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.checkedMemberships").value(0))
                .andExpect(jsonPath("$.suspendedMembershipIds.length()").value(0));
    }
}
