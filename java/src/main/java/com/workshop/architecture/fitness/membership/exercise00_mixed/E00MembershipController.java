package com.workshop.architecture.fitness.membership.exercise00_mixed;

import com.workshop.architecture.fitness.customer.CustomerEntity;
import com.workshop.architecture.fitness.customer.CustomerRepository;
import com.workshop.architecture.fitness.email.InMemoryEmailService;
import com.workshop.architecture.fitness.external_invoice_provider.ExternalInvoiceProviderResponse;
import com.workshop.architecture.fitness.external_invoice_provider.ExternalInvoiceProviderStatus;
import com.workshop.architecture.fitness.external_invoice_provider.ExternalInvoiceProviderUpsertRequest;
import com.workshop.architecture.fitness.plan.PlanEntity;
import com.workshop.architecture.fitness.plan.PlanRepository;
import jakarta.validation.Valid;
import java.time.LocalDate;
import java.time.Period;
import java.util.Map;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClient;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/e00/memberships")
public class E00MembershipController {

    private final E00MembershipRepository membershipRepository;
    private final CustomerRepository customerRepository;
    private final PlanRepository planRepository;
    private final InMemoryEmailService emailService;
    private final RestClient restClient;
    private final String billingSenderEmailAddress;

    public E00MembershipController(
            E00MembershipRepository membershipRepository,
            CustomerRepository customerRepository,
            PlanRepository planRepository,
            InMemoryEmailService emailService,
            RestClient.Builder restClientBuilder,
            @Value("${workshop.external-invoice-provider.base-url}") String externalInvoiceProviderBaseUrl,
            @Value("${workshop.billing.sender-email-address}") String billingSenderEmailAddress
    ) {
        this.membershipRepository = membershipRepository;
        this.customerRepository = customerRepository;
        this.planRepository = planRepository;
        this.emailService = emailService;
        this.restClient = restClientBuilder.baseUrl(externalInvoiceProviderBaseUrl).build();
        this.billingSenderEmailAddress = billingSenderEmailAddress;
    }

    @PostMapping("/activate")
    E00ActivateMembershipResponse activateMembership(@Valid @RequestBody E00ActivateMembershipRequest request) {
        CustomerEntity customer;
        PlanEntity plan;
        E00MembershipEntity membership;
        E00Invoice invoice;
        String email;
        LocalDate startDate;
        LocalDate endDate;

        customer = customerRepository.findById(UUID.fromString(request.customerId()))
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Customer %s was not found".formatted(request.customerId())
                ));

        plan = planRepository.findById(UUID.fromString(request.planId()))
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Plan %s was not found".formatted(request.planId())
                ));

        startDate = LocalDate.now();
        endDate = startDate.plusMonths(plan.getDurationInMonths());

        if (Period.between(customer.getDateOfBirth(), startDate).getYears() < 18
                && !Boolean.TRUE.equals(request.signedByCustodian())) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "Customers younger than 18 require signedByCustodian=true"
            );
        }

        membership = membershipRepository.save(new E00MembershipEntity(
                UUID.randomUUID(),
                request.customerId(),
                request.planId(),
                plan.getPrice().intValue(),
                plan.getDurationInMonths(),
                "ACTIVE",
                startDate,
                endDate
        ));

        invoice = new E00Invoice(
                UUID.randomUUID().toString(),
                membership.getId().toString(),
                request.customerId(),
                membership.getPlanPrice(),
                LocalDate.now().plusDays(30)
        );


        var externalInvoice = restClient.post()
                .uri("/api/shared/external-invoice-provider/invoices")
                .contentType(MediaType.APPLICATION_JSON)
                .body(new ExternalInvoiceProviderUpsertRequest(
                        invoice.customerId(),
                        invoice.membershipId(),
                        invoice.amount(),
                        "CHF",
                        invoice.dueDate(),
                        ExternalInvoiceProviderStatus.OPEN,
                        "Membership invoice for %s".formatted(plan.getTitle()),
                        invoice.id(),
                        Map.of(
                                "exercise", "e00",
                                "planId", membership.getPlanId()
                        )
                ))
                .retrieve()
                .body(ExternalInvoiceProviderResponse.class);

        email = """
                |
                |To: %s
                |From: %s
                |Subject: Your Membership Invoice %s
                |
                |Dear customer,
                |
                |Thank you for your membership.
                |
                |Please find your invoice details below:
                |Invoice ID: %s
                |Amount Due: CHF %s
                |Due Date: %s
                |
                |Attachment: invoice-%s.pdf
                |
                |Kind regards,
                |Codeartify Billing
                |
                """.formatted(
                customer.getEmailAddress(),
                billingSenderEmailAddress,
                invoice.id(),
                invoice.id(),
                invoice.amount(),
                invoice.dueDate(),
                invoice.id()
        ).replace("\n|", "\n").trim();

        System.out.println(email);

        emailService.send(email);

        return new E00ActivateMembershipResponse(
                membership.getId().toString(),
                membership.getCustomerId(),
                membership.getPlanId(),
                membership.getPlanPrice(),
                membership.getPlanDuration(),
                membership.getStatus(),
                membership.getStartDate(),
                membership.getEndDate(),
                invoice.id(),
                externalInvoice == null ? null : externalInvoice.invoiceId(),
                invoice.dueDate()
        );
    }
}
