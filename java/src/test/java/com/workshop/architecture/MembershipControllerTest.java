package com.workshop.architecture;

import com.workshop.architecture.external_invoice_provider.InvoiceProviderStore;
import com.workshop.architecture.fitness.managing_memberships.shared.InMemoryEmailService;
import com.workshop.architecture.fitness.managing_memberships.activate_membership.ActivateMembershipResponse;
import com.workshop.architecture.fitness.managing_memberships.get_membership.GetMembershipResponse;
import com.workshop.architecture.fitness.managing_memberships.list_memberships.ListMembershipResponse;
import com.workshop.architecture.fitness.managing_memberships.shared.MembershipBillingReferenceEntity;
import com.workshop.architecture.fitness.managing_memberships.shared.MembershipBillingReferenceRepository;
import com.workshop.architecture.fitness.managing_memberships.shared.MembershipEntity;
import com.workshop.architecture.fitness.managing_memberships.shared.MembershipRepository;
import com.workshop.architecture.fitness.managing_memberships.suspend_membership.SuspendOverdueMembershipsResponse;
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

import java.io.IOException;
import java.net.ServerSocket;
import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.DEFINED_PORT)
class MembershipControllerTest {

    private static final int TEST_PORT = findFreePort();
    private static final String MEMBERSHIPS_BASE_PATH = "/api/memberships";

    @DynamicPropertySource
    static void registerProperties(DynamicPropertyRegistry registry) {
        registry.add("server.port", () -> TEST_PORT);
        registry.add("workshop.external-invoice-provider.base-url", () -> "http://localhost:" + TEST_PORT);
        registry.add("spring.datasource.url", () -> "jdbc:h2:mem:membership-test;DB_CLOSE_DELAY=-1");
        registry.add("spring.jpa.hibernate.ddl-auto", () -> "create-drop");
    }

    @LocalServerPort
    private int serverPort;

    @Autowired
    private MembershipRepository membershipRepository;

    @Autowired
    private MembershipBillingReferenceRepository billingReferenceRepository;

    @Autowired
    private InvoiceProviderStore externalInvoiceProviderStore;

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

        ActivateMembershipResponse response = client.post()
                .uri(MEMBERSHIPS_BASE_PATH + "/activate")
                .contentType(MediaType.APPLICATION_JSON)
                .body("""
                        {
                          "customerId": "11111111-1111-1111-1111-111111111111",
                          "planId": "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                          "signedByCustodian": false
                        }
                        """)
                .retrieve()
                .body(ActivateMembershipResponse.class);

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
    void activateMembershipRejectsMinorWithoutCustodianSignature() {
        RestClient client = RestClient.builder()
                .baseUrl("http://localhost:" + serverPort)
                .build();

        assertThatThrownBy(() -> client.post()
                .uri(MEMBERSHIPS_BASE_PATH + "/activate")
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
    void listMembershipsReturnsAllMemberships() {
        MembershipEntity activeMembership = membershipRepository.save(new MembershipEntity(
                UUID.fromString("b7000000-0000-0000-0000-000000000001"),
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
                UUID.fromString("b7000000-0000-0000-0000-000000000002"),
                "22222222-2222-2222-2222-222222222222",
                "aaaaaa24-aaaa-aaaa-aaaa-aaaaaaaaaa24",
                1699,
                24,
                "SUSPENDED",
                "NON_PAYMENT",
                LocalDate.parse("2026-01-01"),
                LocalDate.parse("2028-01-01")
        ));

        RestClient client = RestClient.builder()
                .baseUrl("http://localhost:" + serverPort)
                .build();

        ListMembershipResponse[] response = client.get()
                .uri(MEMBERSHIPS_BASE_PATH)
                .retrieve()
                .body(ListMembershipResponse[].class);

        assertThat(response).isNotNull();
        assertThat(response).hasSize(2);
        assertThat(response)
                .extracting(ListMembershipResponse::membershipId)
                .containsExactlyInAnyOrder(
                        activeMembership.getId().toString(),
                        suspendedMembership.getId().toString()
                );
        assertThat(response)
                .extracting(ListMembershipResponse::status)
                .containsExactlyInAnyOrder("ACTIVE", "SUSPENDED");
    }

    @Test
    void getMembershipReturnsMembershipById() {
        MembershipEntity membership = membershipRepository.save(new MembershipEntity(
                UUID.fromString("b7000000-0000-0000-0000-000000000003"),
                "33333333-3333-3333-3333-333333333333",
                "aaaaaaa6-aaaa-aaaa-aaaa-aaaaaaaaaaa6",
                599,
                6,
                "ACTIVE",
                null,
                LocalDate.parse("2026-02-01"),
                LocalDate.parse("2026-08-01")
        ));

        RestClient client = RestClient.builder()
                .baseUrl("http://localhost:" + serverPort)
                .build();

        GetMembershipResponse response = client.get()
                .uri(MEMBERSHIPS_BASE_PATH + "/{membershipId}", membership.getId())
                .retrieve()
                .body(GetMembershipResponse.class);

        assertThat(response).isNotNull();
        assertThat(response.membershipId()).isEqualTo(membership.getId().toString());
        assertThat(response.customerId()).isEqualTo("33333333-3333-3333-3333-333333333333");
        assertThat(response.planId()).isEqualTo("aaaaaaa6-aaaa-aaaa-aaaa-aaaaaaaaaaa6");
        assertThat(response.planPrice()).isEqualTo(599);
        assertThat(response.planDuration()).isEqualTo(6);
        assertThat(response.status()).isEqualTo("ACTIVE");
        assertThat(response.reason()).isNull();
        assertThat(response.startDate()).isEqualTo(LocalDate.parse("2026-02-01"));
        assertThat(response.endDate()).isEqualTo(LocalDate.parse("2026-08-01"));
    }

    @Test
    void suspendOverdueMembershipsSuspendsOnlyActiveMembershipsWithOverdueOpenInvoices() {
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
        MembershipEntity activeNotOverdueMembership = membershipRepository.save(new MembershipEntity(
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
        MembershipEntity suspendedMembership = membershipRepository.save(new MembershipEntity(
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
                "external-overdue-1",
                "corr-overdue-1",
                LocalDate.parse("2026-04-01"),
                "OPEN",
                Instant.parse("2026-01-01T10:00:00Z"),
                Instant.parse("2026-01-01T10:00:00Z")
        ));
        billingReferenceRepository.save(new MembershipBillingReferenceEntity(
                UUID.randomUUID(),
                activeNotOverdueMembership.getId(),
                "external-future-1",
                "corr-future-1",
                LocalDate.parse("2026-05-10"),
                "OPEN",
                Instant.parse("2026-01-01T10:00:00Z"),
                Instant.parse("2026-01-01T10:00:00Z")
        ));
        billingReferenceRepository.save(new MembershipBillingReferenceEntity(
                UUID.randomUUID(),
                activePaidMembership.getId(),
                "external-paid-1",
                "corr-paid-1",
                LocalDate.parse("2026-04-01"),
                "PAID",
                Instant.parse("2026-01-01T10:00:00Z"),
                Instant.parse("2026-01-01T10:00:00Z")
        ));
        billingReferenceRepository.save(new MembershipBillingReferenceEntity(
                UUID.randomUUID(),
                suspendedMembership.getId(),
                "external-suspended-1",
                "corr-suspended-1",
                LocalDate.parse("2026-04-01"),
                "OPEN",
                Instant.parse("2026-01-01T10:00:00Z"),
                Instant.parse("2026-01-01T10:00:00Z")
        ));
        billingReferenceRepository.save(new MembershipBillingReferenceEntity(
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

        SuspendOverdueMembershipsResponse response = client.post()
                .uri(MEMBERSHIPS_BASE_PATH + "/suspend-overdue")
                .contentType(MediaType.APPLICATION_JSON)
                .body("""
                        {
                          "checkedAt": "2026-04-27T10:00:00Z"
                        }
                        """)
                .retrieve()
                .body(SuspendOverdueMembershipsResponse.class);

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
