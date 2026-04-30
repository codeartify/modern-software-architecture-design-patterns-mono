package com.workshop.architecture;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.workshop.architecture.fitness.*;
import com.workshop.architecture.external_invoice_provider.InvoiceProviderStore;
import java.io.IOException;
import java.net.ServerSocket;
import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.http.MediaType;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientResponseException;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.DEFINED_PORT)
class MembershipLifecycleControllerTest {

    private static final int TEST_PORT = findFreePort();
    private static final String MEMBERSHIPS_BASE_PATH = "/api/memberships";

    @DynamicPropertySource
    static void registerProperties(DynamicPropertyRegistry registry) {
        registry.add("server.port", () -> TEST_PORT);
        registry.add("workshop.external-invoice-provider.base-url", () -> "http://localhost:" + TEST_PORT);
        registry.add("spring.datasource.url", () -> "jdbc:h2:mem:membership-lifecycle-test;DB_CLOSE_DELAY=-1");
        registry.add("spring.jpa.hibernate.ddl-auto", () -> "create-drop");
    }

    @LocalServerPort
    private int serverPort;

    @Autowired
    private MembershipRepository membershipRepository;

    @Autowired
    private MembershipBillingReferenceRepository billingReferenceRepository;

    @Autowired
    private InvoiceProviderStore invoiceProviderStore;

    @Autowired
    private InMemoryEmailService emailService;

    private RestClient client;

    @BeforeEach
    void setUp() {
        billingReferenceRepository.deleteAll();
        membershipRepository.deleteAll();
        invoiceProviderStore.clear();
        emailService.clear();
        client = RestClient.builder()
                .baseUrl("http://localhost:" + serverPort)
                .build();
    }

    @Test
    void activeMembershipCanBePausedAndExtendsEndDateWithoutBillingOrEmail() {
        MembershipEntity membership = saveMembership("ACTIVE", null, LocalDate.parse("2027-01-31"));
        billingReferenceRepository.save(newBillingReference(membership.getId(), "pause"));

        PauseMembershipResponse response = client.post()
                .uri(MEMBERSHIPS_BASE_PATH + "/{membershipId}/pause", membership.getId())
                .contentType(MediaType.APPLICATION_JSON)
                .body("""
                        {
                          "pauseStartDate": "2026-06-01",
                          "pauseEndDate": "2026-06-14",
                          "reason": "Vacation"
                        }
                        """)
                .retrieve()
                .body(PauseMembershipResponse.class);

        MembershipEntity updatedMembership = membershipRepository.findById(membership.getId()).orElseThrow();

        assertThat(response).isNotNull();
        assertThat(response.previousStatus()).isEqualTo("ACTIVE");
        assertThat(response.newStatus()).isEqualTo("PAUSED");
        assertThat(response.previousEndDate()).isEqualTo(LocalDate.parse("2027-01-31"));
        assertThat(response.newEndDate()).isEqualTo(LocalDate.parse("2027-02-14"));
        assertThat(updatedMembership.getStatus()).isEqualTo("PAUSED");
        assertThat(updatedMembership.getPauseStartDate()).isEqualTo(LocalDate.parse("2026-06-01"));
        assertThat(updatedMembership.getPauseEndDate()).isEqualTo(LocalDate.parse("2026-06-14"));
        assertThat(updatedMembership.getPauseReason()).isEqualTo("Vacation");
        assertThat(billingReferenceRepository.findAll()).hasSize(1);
        assertThat(invoiceProviderStore.findAll()).isEmpty();
        assertThat(emailService.sentEmails()).isEmpty();
    }

    @Test
    void pauseRejectsInvalidStatusesAndDateRange() {
        MembershipEntity suspendedMembership = saveMembership("SUSPENDED", "NON_PAYMENT", LocalDate.parse("2027-01-31"));
        MembershipEntity cancelledMembership = saveMembership("CANCELLED", null, LocalDate.parse("2027-01-31"));
        MembershipEntity activeMembership = saveMembership("ACTIVE", null, LocalDate.parse("2027-01-31"));

        assertBadRequest(
                () -> client.post()
                        .uri(MEMBERSHIPS_BASE_PATH + "/{membershipId}/pause", suspendedMembership.getId())
                        .contentType(MediaType.APPLICATION_JSON)
                        .body("""
                                {
                                  "pauseStartDate": "2026-06-01",
                                  "pauseEndDate": "2026-06-14"
                                }
                                """)
                        .retrieve()
                        .toBodilessEntity(),
                "Only active memberships can be paused"
        );

        assertBadRequest(
                () -> client.post()
                        .uri(MEMBERSHIPS_BASE_PATH + "/{membershipId}/pause", cancelledMembership.getId())
                        .contentType(MediaType.APPLICATION_JSON)
                        .body("""
                                {
                                  "pauseStartDate": "2026-06-01",
                                  "pauseEndDate": "2026-06-14"
                                }
                                """)
                        .retrieve()
                        .toBodilessEntity(),
                "Only active memberships can be paused"
        );

        assertBadRequest(
                () -> client.post()
                        .uri(MEMBERSHIPS_BASE_PATH + "/{membershipId}/pause", activeMembership.getId())
                        .contentType(MediaType.APPLICATION_JSON)
                        .body("""
                                {
                                  "pauseStartDate": "2026-06-14",
                                  "pauseEndDate": "2026-06-01"
                                }
                                """)
                        .retrieve()
                        .toBodilessEntity(),
                "pauseEndDate must not be before pauseStartDate"
        );
    }

    @Test
    void pausedMembershipCanBeResumedWithoutChangingEndDateOrBilling() {
        MembershipEntity membership = saveMembership("ACTIVE", null, LocalDate.parse("2027-01-31"));
        membership.pause(LocalDate.parse("2026-06-01"), LocalDate.parse("2026-06-14"), "Vacation");
        membership = membershipRepository.save(membership);
        billingReferenceRepository.save(newBillingReference(membership.getId(), "resume"));

        ResumeMembershipResponse response = client.post()
                .uri(MEMBERSHIPS_BASE_PATH + "/{membershipId}/resume", membership.getId())
                .contentType(MediaType.APPLICATION_JSON)
                .body("""
                        {
                          "resumedAt": "2026-06-10T10:00:00Z",
                          "reason": "Back early"
                        }
                        """)
                .retrieve()
                .body(ResumeMembershipResponse.class);

        MembershipEntity updatedMembership = membershipRepository.findById(membership.getId()).orElseThrow();

        assertThat(response).isNotNull();
        assertThat(response.previousStatus()).isEqualTo("PAUSED");
        assertThat(response.newStatus()).isEqualTo("ACTIVE");
        assertThat(response.previousPauseStartDate()).isEqualTo(LocalDate.parse("2026-06-01"));
        assertThat(response.previousPauseEndDate()).isEqualTo(LocalDate.parse("2026-06-14"));
        assertThat(response.endDate()).isEqualTo(LocalDate.parse("2027-02-14"));
        assertThat(updatedMembership.getStatus()).isEqualTo("ACTIVE");
        assertThat(updatedMembership.getPauseStartDate()).isNull();
        assertThat(updatedMembership.getPauseEndDate()).isNull();
        assertThat(updatedMembership.getPauseReason()).isNull();
        assertThat(billingReferenceRepository.findAll()).hasSize(1);
        assertThat(invoiceProviderStore.findAll()).isEmpty();
        assertThat(emailService.sentEmails()).isEmpty();
    }

    @Test
    void resumeRejectsNonPausedMemberships() {
        MembershipEntity membership = saveMembership("ACTIVE", null, LocalDate.parse("2027-01-31"));

        assertBadRequest(
                () -> client.post()
                        .uri(MEMBERSHIPS_BASE_PATH + "/{membershipId}/resume", membership.getId())
                        .contentType(MediaType.APPLICATION_JSON)
                        .body("{}")
                        .retrieve()
                        .toBodilessEntity(),
                "Only paused memberships can be resumed"
        );
    }

    @Test
    void pauseResumeAndExtendRejectExpiredMemberships() {
        MembershipEntity activeExpiredMembership = saveMembership("ACTIVE", null, LocalDate.parse("2025-12-31"));
        MembershipEntity pausedExpiredMembership = saveMembership("ACTIVE", null, LocalDate.parse("2025-12-31"));
        pausedExpiredMembership.pause(
                LocalDate.parse("2025-06-01"),
                LocalDate.parse("2025-06-14"),
                "Expired pause"
        );
        pausedExpiredMembership = membershipRepository.save(pausedExpiredMembership);

        UUID activeExpiredMembershipId = activeExpiredMembership.getId();
        UUID pausedExpiredMembershipId = pausedExpiredMembership.getId();

        assertBadRequest(
                () -> client.post()
                        .uri(MEMBERSHIPS_BASE_PATH + "/{membershipId}/pause", activeExpiredMembershipId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .body("""
                                {
                                  "pauseStartDate": "2026-06-01",
                                  "pauseEndDate": "2026-06-14"
                                }
                                """)
                        .retrieve()
                        .toBodilessEntity(),
                "Expired memberships cannot be paused"
        );

        assertBadRequest(
                () -> client.post()
                        .uri(MEMBERSHIPS_BASE_PATH + "/{membershipId}/resume", pausedExpiredMembershipId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .body("{}")
                        .retrieve()
                        .toBodilessEntity(),
                "Expired memberships cannot be resumed"
        );

        assertBadRequest(
                () -> client.post()
                        .uri(MEMBERSHIPS_BASE_PATH + "/{membershipId}/extend", activeExpiredMembershipId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .body("""
                                {
                                  "additionalDays": 10
                                }
                                """)
                        .retrieve()
                        .toBodilessEntity(),
                "Expired memberships cannot be extended"
        );
    }

    @Test
    void membershipCanBeCancelledFromPausedAndCannotBeCancelledAgain() {
        MembershipEntity membership = saveMembership("ACTIVE", null, LocalDate.parse("2027-01-31"));
        membership.pause(LocalDate.parse("2026-06-01"), LocalDate.parse("2026-06-14"), "Vacation");
        membership = membershipRepository.save(membership);
        UUID membershipId = membership.getId();

        CancelMembershipResponse response = client.post()
                .uri(MEMBERSHIPS_BASE_PATH + "/{membershipId}/cancel", membership.getId())
                .contentType(MediaType.APPLICATION_JSON)
                .body("""
                        {
                          "cancelledAt": "2026-06-15T10:00:00Z",
                          "reason": "Moving away"
                        }
                        """)
                .retrieve()
                .body(CancelMembershipResponse.class);

        assertThat(response).isNotNull();
        assertThat(response.previousStatus()).isEqualTo("PAUSED");
        assertThat(response.newStatus()).isEqualTo("CANCELLED");
        assertThat(response.reason()).isEqualTo("Moving away");
        assertThat(membershipRepository.findById(membership.getId()).orElseThrow().getStatus())
                .isEqualTo("CANCELLED");
        assertThat(invoiceProviderStore.findAll()).isEmpty();
        assertThat(emailService.sentEmails()).isEmpty();

        assertBadRequest(
                () -> client.post()
                        .uri(MEMBERSHIPS_BASE_PATH + "/{membershipId}/cancel", membershipId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .body("{}")
                        .retrieve()
                        .toBodilessEntity(),
                "Membership is already cancelled"
        );
    }

    @Test
    void paymentForCancelledMembershipMarksBillingPaidButDoesNotReactivate() {
        MembershipEntity membership = saveMembership("CANCELLED", null, LocalDate.parse("2027-01-31"));
        MembershipBillingReferenceEntity billingReference = billingReferenceRepository.save(
                newBillingReference(membership.getId(), "cancelled-payment")
        );

        PaymentReceivedResponse response = client.post()
                .uri(MEMBERSHIPS_BASE_PATH + "/payment-received")
                .contentType(MediaType.APPLICATION_JSON)
                .body("""
                        {
                          "externalInvoiceId": "external-cancelled-payment",
                          "paidAt": "2026-06-15T10:00:00Z"
                        }
                        """)
                .retrieve()
                .body(PaymentReceivedResponse.class);

        assertThat(response).isNotNull();
        assertThat(response.previousMembershipStatus()).isEqualTo("CANCELLED");
        assertThat(response.newMembershipStatus()).isEqualTo("CANCELLED");
        assertThat(response.reactivated()).isFalse();
        assertThat(response.message()).isEqualTo("Payment recorded; membership is cancelled and remains unchanged");
        assertThat(membershipRepository.findById(membership.getId()).orElseThrow().getStatus())
                .isEqualTo("CANCELLED");
        assertThat(billingReferenceRepository.findById(billingReference.getId()).orElseThrow().getStatus())
                .isEqualTo("PAID");
    }

    @Test
    void nonBillableExtensionChangesOnlyEndDateAndPreservesStatus() {
        MembershipEntity membership = saveMembership("PAUSED", null, LocalDate.parse("2027-01-31"));
        billingReferenceRepository.save(newBillingReference(membership.getId(), "extension-existing"));

        ExtendMembershipResponse response = client.post()
                .uri(MEMBERSHIPS_BASE_PATH + "/{membershipId}/extend", membership.getId())
                .contentType(MediaType.APPLICATION_JSON)
                .body("""
                        {
                          "additionalMonths": 1,
                          "additionalDays": 5,
                          "billable": false,
                          "reason": "Goodwill"
                        }
                        """)
                .retrieve()
                .body(ExtendMembershipResponse.class);

        assertThat(response).isNotNull();
        assertThat(response.status()).isEqualTo("PAUSED");
        assertThat(response.previousEndDate()).isEqualTo(LocalDate.parse("2027-01-31"));
        assertThat(response.newEndDate()).isEqualTo(LocalDate.parse("2027-03-05"));
        assertThat(response.billable()).isFalse();
        assertThat(response.billingReferenceId()).isNull();
        assertThat(billingReferenceRepository.findAll()).hasSize(1);
        assertThat(invoiceProviderStore.findAll()).isEmpty();
        assertThat(emailService.sentEmails()).isEmpty();
    }

    @Test
    void billableExtensionCreatesExternalInvoiceAndBillingReference() {
        MembershipEntity membership = saveMembership("SUSPENDED", "NON_PAYMENT", LocalDate.parse("2027-01-31"));

        ExtendMembershipResponse response = client.post()
                .uri(MEMBERSHIPS_BASE_PATH + "/{membershipId}/extend", membership.getId())
                .contentType(MediaType.APPLICATION_JSON)
                .body("""
                        {
                          "additionalDays": 10,
                          "billable": true,
                          "price": 250,
                          "reason": "Manual billable extension"
                        }
                        """)
                .retrieve()
                .body(ExtendMembershipResponse.class);

        assertThat(response).isNotNull();
        assertThat(response.status()).isEqualTo("SUSPENDED");
        assertThat(response.newEndDate()).isEqualTo(LocalDate.parse("2027-02-10"));
        assertThat(response.billable()).isTrue();
        assertThat(response.billingReferenceId()).isNotBlank();
        assertThat(response.externalInvoiceReference()).isNotBlank();
        assertThat(response.externalInvoiceId()).isNotBlank();
        assertThat(billingReferenceRepository.findAll()).hasSize(1);
        assertThat(invoiceProviderStore.findAll()).hasSize(1);
        assertThat(invoiceProviderStore.findAll().getFirst().amountInCents()).isEqualTo(250);
        assertThat(emailService.sentEmails()).isEmpty();
    }

    @Test
    void extensionRejectsCancelledInvalidDurationAndBillableWithoutPrice() {
        MembershipEntity cancelledMembership = saveMembership("CANCELLED", null, LocalDate.parse("2027-01-31"));
        MembershipEntity activeMembership = saveMembership("ACTIVE", null, LocalDate.parse("2027-01-31"));

        assertBadRequest(
                () -> client.post()
                        .uri(MEMBERSHIPS_BASE_PATH + "/{membershipId}/extend", cancelledMembership.getId())
                        .contentType(MediaType.APPLICATION_JSON)
                        .body("""
                                {
                                  "additionalDays": 10
                                }
                                """)
                        .retrieve()
                        .toBodilessEntity(),
                "Cancelled memberships cannot be extended"
        );

        assertBadRequest(
                () -> client.post()
                        .uri(MEMBERSHIPS_BASE_PATH + "/{membershipId}/extend", activeMembership.getId())
                        .contentType(MediaType.APPLICATION_JSON)
                        .body("""
                                {
                                  "additionalDays": 0
                                }
                                """)
                        .retrieve()
                        .toBodilessEntity(),
                "Extension duration must be positive"
        );

        assertBadRequest(
                () -> client.post()
                        .uri(MEMBERSHIPS_BASE_PATH + "/{membershipId}/extend", activeMembership.getId())
                        .contentType(MediaType.APPLICATION_JSON)
                        .body("""
                                {
                                  "additionalDays": 10,
                                  "billable": true
                                }
                                """)
                        .retrieve()
                        .toBodilessEntity(),
                "Billable extensions require a positive price"
        );
    }

    private MembershipEntity saveMembership(String status, String reason, LocalDate endDate) {
        return membershipRepository.save(new MembershipEntity(
                UUID.randomUUID(),
                "11111111-1111-1111-1111-111111111111",
                "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                999,
                12,
                status,
                reason,
                LocalDate.parse("2026-01-01"),
                endDate
        ));
    }

    private MembershipBillingReferenceEntity newBillingReference(UUID membershipId, String suffix) {
        return new MembershipBillingReferenceEntity(
                UUID.randomUUID(),
                membershipId,
                "external-" + suffix,
                "local-" + suffix,
                LocalDate.parse("2026-06-01"),
                "OPEN",
                Instant.parse("2026-01-01T10:00:00Z"),
                Instant.parse("2026-01-01T10:00:00Z")
        );
    }

    private void assertBadRequest(Runnable request, String expectedMessage) {
        assertThatThrownBy(request::run)
                .isInstanceOf(RestClientResponseException.class)
                .satisfies(error -> {
                    RestClientResponseException responseException = (RestClientResponseException) error;
                    assertThat(responseException.getStatusCode().value()).isEqualTo(400);
                    assertThat(responseException.getResponseBodyAsString()).contains(expectedMessage);
                });
    }

    private static int findFreePort() {
        try (ServerSocket socket = new ServerSocket(0)) {
            socket.setReuseAddress(true);
            return socket.getLocalPort();
        } catch (IOException exception) {
            throw new IllegalStateException("Could not allocate a free TCP port for the test", exception);
        }
    }
}
