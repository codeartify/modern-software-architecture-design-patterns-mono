package com.workshop.architecture.fitness.membership.exercise00_mixed;

import static org.assertj.core.api.Assertions.assertThat;

import com.workshop.architecture.fitness.email.InMemoryEmailService;
import com.workshop.architecture.fitness.external_invoice_provider.ExternalInvoiceProviderStore;
import java.io.IOException;
import java.net.ServerSocket;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.http.MediaType;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.web.client.RestClient;

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
    private ExternalInvoiceProviderStore externalInvoiceProviderStore;

    @Autowired
    private InMemoryEmailService emailService;

    @BeforeEach
    void clearState() {
        membershipRepository.deleteAll();
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
                          "planId": "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12"
                        }
                        """)
                .retrieve()
                .body(E00ActivateMembershipResponse.class);

        assertThat(response).isNotNull();
        assertThat(response.planPrice()).isEqualTo(999);
        assertThat(response.planDuration()).isEqualTo(12);
        assertThat(membershipRepository.findAll()).hasSize(1);
        assertThat(externalInvoiceProviderStore.findAll()).hasSize(1);
        assertThat(externalInvoiceProviderStore.findAll().getFirst().contractReference())
                .isEqualTo(response.membershipId());
        assertThat(emailService.sentEmails()).hasSize(1);
        assertThat(emailService.sentEmails().getFirst()).contains("billing@codeartify.com");
        assertThat(emailService.sentEmails().getFirst()).contains(response.invoiceId());
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
