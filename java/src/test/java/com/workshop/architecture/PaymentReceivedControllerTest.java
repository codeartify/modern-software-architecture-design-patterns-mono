package com.workshop.architecture;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;

import com.workshop.architecture.fitness.shared.MembershipBillingReferenceEntity;
import com.workshop.architecture.fitness.shared.MembershipBillingReferenceRepository;
import com.workshop.architecture.fitness.shared.MembershipEntity;
import com.workshop.architecture.fitness.shared.MembershipRepository;
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
class PaymentReceivedControllerTest {

    @DynamicPropertySource
    static void registerProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", () -> "jdbc:h2:mem:membership-payment-received-test;DB_CLOSE_DELAY=-1");
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
    void paidCallbackForActiveMembershipMarksBillingReferencePaidWithoutChangingMembership() throws Exception {
        UUID membershipId = UUID.randomUUID();
        MembershipEntity membership = membershipRepository.save(new MembershipEntity(
                membershipId,
                "11111111-1111-1111-1111-111111111111",
                "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                999,
                12,
                "ACTIVE",
                null,
                LocalDate.parse("2026-01-01"),
                LocalDate.parse("2027-01-01")
        ));
        MembershipBillingReferenceEntity billingReference = billingReferenceRepository.save(
                new MembershipBillingReferenceEntity(
                        UUID.randomUUID(),
                        membershipId,
                        "external-001",
                        "local-001",
                        LocalDate.parse("2026-02-01"),
                        "OPEN",
                        Instant.parse("2026-01-01T10:00:00Z"),
                        Instant.parse("2026-01-01T10:00:00Z")
                )
        );

        mockMvc.perform(post("/api/memberships/payment-received")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "externalInvoiceId": "external-001",
                                  "paidAt": "2026-01-15T10:00:00Z"
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.membershipId").value(membership.getId().toString()))
                .andExpect(jsonPath("$.billingReferenceId").value(billingReference.getId().toString()))
                .andExpect(jsonPath("$.previousMembershipStatus").value("ACTIVE"))
                .andExpect(jsonPath("$.newMembershipStatus").value("ACTIVE"))
                .andExpect(jsonPath("$.reactivated").value(false))
                .andExpect(jsonPath("$.message").value("Payment recorded; membership status unchanged"));

        MembershipBillingReferenceEntity updatedBillingReference = billingReferenceRepository.findById(
                billingReference.getId()
        ).orElseThrow();
        MembershipEntity updatedMembership = membershipRepository.findById(membership.getId()).orElseThrow();

        org.assertj.core.api.Assertions.assertThat(updatedBillingReference.getStatus()).isEqualTo("PAID");
        org.assertj.core.api.Assertions.assertThat(updatedMembership.getStatus()).isEqualTo("ACTIVE");
    }

    @Test
    void paidCallbackReactivatesMembershipSuspendedForNonPaymentWithinMembershipPeriod() throws Exception {
        UUID membershipId = UUID.randomUUID();
        MembershipEntity membership = membershipRepository.save(new MembershipEntity(
                membershipId,
                "11111111-1111-1111-1111-111111111111",
                "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                999,
                12,
                "SUSPENDED",
                "NON_PAYMENT",
                LocalDate.parse("2026-01-01"),
                LocalDate.parse("2027-01-01")
        ));
        billingReferenceRepository.save(new MembershipBillingReferenceEntity(
                UUID.randomUUID(),
                membershipId,
                "external-002",
                "local-002",
                LocalDate.parse("2026-02-01"),
                "OPEN",
                Instant.parse("2026-01-01T10:00:00Z"),
                Instant.parse("2026-01-01T10:00:00Z")
        ));

        mockMvc.perform(post("/api/memberships/payment-received")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "externalInvoiceReference": "local-002",
                                  "paidAt": "2026-02-15T10:00:00Z"
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.previousMembershipStatus").value("SUSPENDED"))
                .andExpect(jsonPath("$.newMembershipStatus").value("ACTIVE"))
                .andExpect(jsonPath("$.reactivated").value(true))
                .andExpect(jsonPath("$.message").value("Payment recorded; membership reactivated"));

        MembershipEntity updatedMembership = membershipRepository.findById(membership.getId()).orElseThrow();
        org.assertj.core.api.Assertions.assertThat(updatedMembership.getStatus()).isEqualTo("ACTIVE");
        org.assertj.core.api.Assertions.assertThat(updatedMembership.getReason()).isNull();
    }

    @Test
    void paidCallbackKeepsMembershipSuspendedWhenMembershipPeriodAlreadyEnded() throws Exception {
        UUID membershipId = UUID.randomUUID();
        membershipRepository.save(new MembershipEntity(
                membershipId,
                "11111111-1111-1111-1111-111111111111",
                "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                999,
                12,
                "SUSPENDED",
                "NON_PAYMENT",
                LocalDate.parse("2025-01-01"),
                LocalDate.parse("2025-12-31")
        ));
        billingReferenceRepository.save(new MembershipBillingReferenceEntity(
                UUID.randomUUID(),
                membershipId,
                "external-003",
                "local-003",
                LocalDate.parse("2025-02-01"),
                "OPEN",
                Instant.parse("2025-01-01T10:00:00Z"),
                Instant.parse("2025-01-01T10:00:00Z")
        ));

        mockMvc.perform(post("/api/memberships/payment-received")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "externalInvoiceId": "external-003",
                                  "paidAt": "2026-01-10T10:00:00Z"
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.reactivated").value(false))
                .andExpect(jsonPath("$.newMembershipStatus").value("SUSPENDED"))
                .andExpect(jsonPath("$.message").value("Payment recorded; membership status unchanged"));
    }

    @Test
    void paidCallbackKeepsMembershipSuspendedWhenSuspendedForAnotherReason() throws Exception {
        UUID membershipId = UUID.randomUUID();
        membershipRepository.save(new MembershipEntity(
                membershipId,
                "11111111-1111-1111-1111-111111111111",
                "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                999,
                12,
                "SUSPENDED",
                "MANUAL_REVIEW",
                LocalDate.parse("2026-01-01"),
                LocalDate.parse("2027-01-01")
        ));
        billingReferenceRepository.save(new MembershipBillingReferenceEntity(
                UUID.randomUUID(),
                membershipId,
                "external-004",
                "local-004",
                LocalDate.parse("2026-02-01"),
                "OPEN",
                Instant.parse("2026-01-01T10:00:00Z"),
                Instant.parse("2026-01-01T10:00:00Z")
        ));

        mockMvc.perform(post("/api/memberships/payment-received")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "externalInvoiceId": "external-004",
                                  "paidAt": "2026-02-10T10:00:00Z"
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.reactivated").value(false))
                .andExpect(jsonPath("$.newMembershipStatus").value("SUSPENDED"))
                .andExpect(jsonPath("$.message").value("Payment recorded; membership status unchanged"));
    }

    @Test
    void paidCallbackKeepsCancelledMembershipCancelled() throws Exception {
        UUID membershipId = UUID.randomUUID();
        membershipRepository.save(new MembershipEntity(
                membershipId,
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
                membershipId,
                "external-005",
                "local-005",
                LocalDate.parse("2026-02-01"),
                "OPEN",
                Instant.parse("2026-01-01T10:00:00Z"),
                Instant.parse("2026-01-01T10:00:00Z")
        ));

        mockMvc.perform(post("/api/memberships/payment-received")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "externalInvoiceId": "external-005",
                                  "paidAt": "2026-02-10T10:00:00Z"
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.newMembershipStatus").value("CANCELLED"))
                .andExpect(jsonPath("$.message")
                        .value("Payment recorded; membership is cancelled and remains unchanged"));
    }

    @Test
    void repeatedPaidCallbackDoesNotDuplicateStateChanges() throws Exception {
        UUID membershipId = UUID.randomUUID();
        MembershipEntity membership = membershipRepository.save(new MembershipEntity(
                membershipId,
                "11111111-1111-1111-1111-111111111111",
                "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                999,
                12,
                "ACTIVE",
                null,
                LocalDate.parse("2026-01-01"),
                LocalDate.parse("2027-01-01")
        ));
        MembershipBillingReferenceEntity billingReference = billingReferenceRepository.save(
                new MembershipBillingReferenceEntity(
                        UUID.randomUUID(),
                        membershipId,
                        "external-006",
                        "local-006",
                        LocalDate.parse("2026-02-01"),
                        "OPEN",
                        Instant.parse("2026-01-01T10:00:00Z"),
                        Instant.parse("2026-01-01T10:00:00Z")
                )
        );

        mockMvc.perform(post("/api/memberships/payment-received")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "externalInvoiceId": "external-006",
                                  "paidAt": "2026-02-10T10:00:00Z"
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.reactivated").value(false))
                .andExpect(jsonPath("$.message").value("Payment recorded; membership status unchanged"));

        mockMvc.perform(post("/api/memberships/payment-received")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "externalInvoiceId": "external-006",
                                  "paidAt": "2026-02-11T10:00:00Z"
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.membershipId").value(membership.getId().toString()))
                .andExpect(jsonPath("$.billingReferenceId").value(billingReference.getId().toString()))
                .andExpect(jsonPath("$.newMembershipStatus").value("ACTIVE"))
                .andExpect(jsonPath("$.reactivated").value(false))
                .andExpect(jsonPath("$.message").value("Payment was already recorded; membership status unchanged"));

        MembershipBillingReferenceEntity updatedBillingReference = billingReferenceRepository.findById(
                billingReference.getId()
        ).orElseThrow();
        org.assertj.core.api.Assertions.assertThat(updatedBillingReference.getStatus()).isEqualTo("PAID");
    }
}
