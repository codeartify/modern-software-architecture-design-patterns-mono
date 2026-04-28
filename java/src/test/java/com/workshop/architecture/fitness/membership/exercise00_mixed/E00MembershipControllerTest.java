package com.workshop.architecture.fitness.membership.exercise00_mixed;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.workshop.architecture.fitness.email.InMemoryEmailService;
import com.workshop.architecture.fitness.external_invoice_provider.ExternalInvoiceProviderStore;
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
class E00MembershipControllerTest {

    private static final int TEST_PORT = findFreePort();

    @DynamicPropertySource
    static void registerProperties(DynamicPropertyRegistry registry) {
        registry.add("server.port", () -> TEST_PORT);
        registry.add("workshop.external-invoice-provider.base-url", () -> "http://localhost:" + TEST_PORT);
        registry.add("spring.datasource.url", () -> "jdbc:h2:mem:e00-mixed-test;DB_CLOSE_DELAY=-1");
        registry.add("spring.jpa.hibernate.ddl-auto", () -> "create-drop");
    }

    @LocalServerPort
    private int serverPort;

    @Autowired
    private E00MembershipRepository membershipRepository;

    @Autowired
    private E00MembershipBillingReferenceRepository billingReferenceRepository;

    @Autowired
    private ExternalInvoiceProviderStore externalInvoiceProviderStore;

    @Autowired
    private InMemoryEmailService emailService;

    @BeforeEach
    void clearState() {
        membershipRepository.deleteAll();
        billingReferenceRepository.deleteAll();
        externalInvoiceProviderStore.clear();
        emailService.clear();
    }

    @Test
    void activateMembershipCreatesMembershipExternalInvoiceAndEmail() {
        RestClient client = RestClient.builder()
                .baseUrl("http://localhost:" + serverPort)
                .build();

        E00ActivateMembershipResponse response = client.post()
                .uri("/api/e00/memberships/activate")
                .contentType(MediaType.APPLICATION_JSON)
                .body("""
                        {
                          "customerId": "11111111-1111-1111-1111-111111111111",
                          "planId": "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                          "signedByCustodian": false
                        }
                        """)
                .retrieve()
                .body(E00ActivateMembershipResponse.class);

        assertThat(response).isNotNull();
        assertThat(response.status()).isEqualTo("ACTIVE");
        assertThat(response.planPrice()).isEqualTo(999);
        assertThat(response.planDuration()).isEqualTo(12);
        assertThat(response.startDate()).isNotNull();
        assertThat(response.endDate()).isEqualTo(response.startDate().plusMonths(12));
        assertThat(membershipRepository.findAll()).hasSize(1);
        assertThat(externalInvoiceProviderStore.findAll()).hasSize(1);
        assertThat(externalInvoiceProviderStore.findAll().getFirst().contractReference())
                .isEqualTo(response.membershipId());
        assertThat(billingReferenceRepository.findAll()).hasSize(1);
        assertThat(billingReferenceRepository.findAll().getFirst().getMembershipId())
                .isEqualTo(UUID.fromString(response.membershipId()));
        assertThat(billingReferenceRepository.findAll().getFirst().getExternalInvoiceId())
                .isEqualTo(response.externalInvoiceId());
        assertThat(billingReferenceRepository.findAll().getFirst().getExternalInvoiceReference())
                .isEqualTo(response.invoiceId());
        assertThat(billingReferenceRepository.findAll().getFirst().getDueDate())
                .isEqualTo(response.invoiceDueDate());
        assertThat(billingReferenceRepository.findAll().getFirst().getStatus()).isEqualTo("OPEN");
        assertThat(emailService.sentEmails()).hasSize(1);
        assertThat(emailService.sentEmails().getFirst()).contains("billing@codeartify.com");
        assertThat(emailService.sentEmails().getFirst()).contains(response.invoiceId());
    }

    @Test
    void suspendMembershipChangesStatusWithoutExtendingRuntime() {
        RestClient client = RestClient.builder()
                .baseUrl("http://localhost:" + serverPort)
                .build();

        E00ActivateMembershipResponse activatedMembership = client.post()
                .uri("/api/e00/memberships/activate")
                .contentType(MediaType.APPLICATION_JSON)
                .body("""
                        {
                          "customerId": "11111111-1111-1111-1111-111111111111",
                          "planId": "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                          "signedByCustodian": false
                        }
                        """)
                .retrieve()
                .body(E00ActivateMembershipResponse.class);

        E00MembershipResponse suspendedMembership = client.post()
                .uri("/api/e00/memberships/{membershipId}/suspend", activatedMembership.membershipId())
                .retrieve()
                .body(E00MembershipResponse.class);

        assertThat(suspendedMembership).isNotNull();
        assertThat(suspendedMembership.status()).isEqualTo("SUSPENDED");
        assertThat(suspendedMembership.startDate()).isEqualTo(activatedMembership.startDate());
        assertThat(suspendedMembership.endDate()).isEqualTo(activatedMembership.endDate());
        assertThat(membershipRepository.findById(java.util.UUID.fromString(activatedMembership.membershipId())))
                .isPresent();
        assertThat(membershipRepository.findById(java.util.UUID.fromString(activatedMembership.membershipId()))
                .orElseThrow()
                .getStatus()).isEqualTo("SUSPENDED");
    }

    @Test
    void suspendMembershipRejectsMembershipThatIsNotActive() {
        RestClient client = RestClient.builder()
                .baseUrl("http://localhost:" + serverPort)
                .build();

        E00ActivateMembershipResponse activatedMembership = client.post()
                .uri("/api/e00/memberships/activate")
                .contentType(MediaType.APPLICATION_JSON)
                .body("""
                        {
                          "customerId": "11111111-1111-1111-1111-111111111111",
                          "planId": "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                          "signedByCustodian": false
                        }
                        """)
                .retrieve()
                .body(E00ActivateMembershipResponse.class);

        client.post()
                .uri("/api/e00/memberships/{membershipId}/suspend", activatedMembership.membershipId())
                .retrieve()
                .body(E00MembershipResponse.class);

        assertThatThrownBy(() -> client.post()
                .uri("/api/e00/memberships/{membershipId}/suspend", activatedMembership.membershipId())
                .retrieve()
                .toBodilessEntity())
                .isInstanceOf(RestClientResponseException.class)
                .satisfies(error -> {
                    RestClientResponseException responseException = (RestClientResponseException) error;
                    assertThat(responseException.getStatusCode().value()).isEqualTo(400);
                    assertThat(responseException.getResponseBodyAsString())
                            .contains("must be ACTIVE to suspend");
                });
    }

    @Test
    void activateMembershipRejectsMinorWithoutCustodianSignature() {
        RestClient client = RestClient.builder()
                .baseUrl("http://localhost:" + serverPort)
                .build();

        assertThatThrownBy(() -> client.post()
                .uri("/api/e00/memberships/activate")
                .contentType(MediaType.APPLICATION_JSON)
                .body("""
                        {
                          "customerId": "44444444-4444-4444-4444-444444444444",
                          "planId": "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12"
                        }
                        """)
                .retrieve()
                .toBodilessEntity())
                .isInstanceOf(RestClientResponseException.class)
                .satisfies(error -> {
                    RestClientResponseException responseException = (RestClientResponseException) error;
                    assertThat(responseException.getStatusCode().value()).isEqualTo(400);
                    assertThat(responseException.getResponseBodyAsString())
                            .contains("Customers younger than 18 require signedByCustodian=true");
                });

        assertThat(membershipRepository.findAll()).isEmpty();
        assertThat(billingReferenceRepository.findAll()).isEmpty();
        assertThat(externalInvoiceProviderStore.findAll()).isEmpty();
        assertThat(emailService.sentEmails()).isEmpty();
    }

    @Test
    void suspendOverdueMembershipsSuspendsOnlyActiveMembershipsWithOverdueOpenInvoices() {
        E00MembershipEntity activeOverdueMembership = membershipRepository.save(new E00MembershipEntity(
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
        E00MembershipEntity activeNotOverdueMembership = membershipRepository.save(new E00MembershipEntity(
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
        E00MembershipEntity activePaidMembership = membershipRepository.save(new E00MembershipEntity(
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
        E00MembershipEntity suspendedMembership = membershipRepository.save(new E00MembershipEntity(
                UUID.randomUUID(),
                "11111111-1111-1111-1111-111111111111",
                "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                999,
                12,
                "SUSPENDED",
                null,
                LocalDate.parse("2026-01-01"),
                LocalDate.parse("2027-01-01")
        ));
        E00MembershipEntity cancelledMembership = membershipRepository.save(new E00MembershipEntity(
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

        billingReferenceRepository.save(new E00MembershipBillingReferenceEntity(
                UUID.randomUUID(),
                activeOverdueMembership.getId(),
                "external-overdue-1",
                "corr-overdue-1",
                LocalDate.parse("2026-04-01"),
                "OPEN",
                Instant.parse("2026-01-01T10:00:00Z"),
                Instant.parse("2026-01-01T10:00:00Z")
        ));
        billingReferenceRepository.save(new E00MembershipBillingReferenceEntity(
                UUID.randomUUID(),
                activeNotOverdueMembership.getId(),
                "external-future-1",
                "corr-future-1",
                LocalDate.parse("2026-05-10"),
                "OPEN",
                Instant.parse("2026-01-01T10:00:00Z"),
                Instant.parse("2026-01-01T10:00:00Z")
        ));
        billingReferenceRepository.save(new E00MembershipBillingReferenceEntity(
                UUID.randomUUID(),
                activePaidMembership.getId(),
                "external-paid-1",
                "corr-paid-1",
                LocalDate.parse("2026-04-01"),
                "PAID",
                Instant.parse("2026-01-01T10:00:00Z"),
                Instant.parse("2026-01-01T10:00:00Z")
        ));
        billingReferenceRepository.save(new E00MembershipBillingReferenceEntity(
                UUID.randomUUID(),
                suspendedMembership.getId(),
                "external-suspended-1",
                "corr-suspended-1",
                LocalDate.parse("2026-04-01"),
                "OPEN",
                Instant.parse("2026-01-01T10:00:00Z"),
                Instant.parse("2026-01-01T10:00:00Z")
        ));
        billingReferenceRepository.save(new E00MembershipBillingReferenceEntity(
                UUID.randomUUID(),
                cancelledMembership.getId(),
                "external-cancelled-1",
                "corr-cancelled-1",
                LocalDate.parse("2026-04-01"),
                "OPEN",
                Instant.parse("2026-01-01T10:00:00Z"),
                Instant.parse("2026-01-01T10:00:00Z")
        ));

        RestClient client = RestClient.builder()
                .baseUrl("http://localhost:" + serverPort)
                .build();

        E00SuspendOverdueMembershipsResponse response = client.post()
                .uri("/api/e00/memberships/suspend-overdue")
                .contentType(MediaType.APPLICATION_JSON)
                .body("""
                        {
                          "checkedAt": "2026-04-27T10:00:00Z"
                        }
                        """)
                .retrieve()
                .body(E00SuspendOverdueMembershipsResponse.class);

        assertThat(response).isNotNull();
        assertThat(response.checkedMemberships()).isEqualTo(3);
        assertThat(response.suspendedMembershipIds()).containsExactly(activeOverdueMembership.getId().toString());
        assertThat(membershipRepository.findById(activeOverdueMembership.getId()).orElseThrow().getStatus())
                .isEqualTo("SUSPENDED");
        assertThat(membershipRepository.findById(activeOverdueMembership.getId()).orElseThrow().getReason())
                .isEqualTo("NON_PAYMENT");
        assertThat(membershipRepository.findById(activeNotOverdueMembership.getId()).orElseThrow().getStatus())
                .isEqualTo("ACTIVE");
        assertThat(membershipRepository.findById(activePaidMembership.getId()).orElseThrow().getStatus())
                .isEqualTo("ACTIVE");
        assertThat(membershipRepository.findById(suspendedMembership.getId()).orElseThrow().getStatus())
                .isEqualTo("SUSPENDED");
        assertThat(membershipRepository.findById(cancelledMembership.getId()).orElseThrow().getStatus())
                .isEqualTo("CANCELLED");
    }

    private static int findFreePort() {
        try (ServerSocket socket = new ServerSocket(0)) {
            return socket.getLocalPort();
        }
        catch (IOException exception) {
            throw new IllegalStateException("Could not allocate a free TCP port for the test", exception);
        }
    }
}
