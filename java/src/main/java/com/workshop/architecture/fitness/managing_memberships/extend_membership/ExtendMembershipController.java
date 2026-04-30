package com.workshop.architecture.fitness.managing_memberships.extend_membership;

import com.workshop.architecture.fitness.managing_memberships.shared.ExternalInvoiceProviderResponse;
import com.workshop.architecture.fitness.managing_memberships.shared.ExternalInvoiceProviderStatus;
import com.workshop.architecture.fitness.managing_memberships.shared.ExternalInvoiceProviderUpsertRequest;
import com.workshop.architecture.fitness.managing_memberships.shared.MembershipBillingReferenceEntity;
import com.workshop.architecture.fitness.managing_memberships.shared.MembershipBillingReferenceRepository;
import com.workshop.architecture.fitness.managing_memberships.shared.MembershipEntity;
import com.workshop.architecture.fitness.managing_memberships.shared.MembershipRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestClient;
import org.springframework.web.server.ResponseStatusException;

import java.time.Instant;
import java.time.LocalDate;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/memberships")
public class ExtendMembershipController {

    private final MembershipRepository membershipRepository;
    private final MembershipBillingReferenceRepository billingReferenceRepository;
    private final RestClient restClient;

    public ExtendMembershipController(
            MembershipRepository membershipRepository,
            MembershipBillingReferenceRepository billingReferenceRepository,
            RestClient.Builder restClientBuilder,
            @Value("${workshop.external-invoice-provider.base-url}") String externalInvoiceProviderBaseUrl
    ) {
        this.membershipRepository = membershipRepository;
        this.billingReferenceRepository = billingReferenceRepository;
        this.restClient = restClientBuilder.baseUrl(externalInvoiceProviderBaseUrl).build();
    }

    @PostMapping("/{membershipId}/extend")
    ExtendMembershipResponse extendMembership(
            @PathVariable String membershipId,
            @RequestBody ExtendMembershipRequest request
    ) {
        MembershipEntity membership;
        MembershipBillingReferenceEntity billingReference;
        int additionalMonths = request.additionalMonths() == null ? 0 : request.additionalMonths();
        int additionalDays = request.additionalDays() == null ? 0 : request.additionalDays();
        boolean billable = Boolean.TRUE.equals(request.billable());
        LocalDate previousEndDate;
        String invoiceId;
        String externalInvoiceId;
        LocalDate invoiceDueDate;
        Instant now;

        membership = membershipRepository.findById(UUID.fromString(membershipId))
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Membership %s was not found".formatted(membershipId)
                ));

        if (membership.isCancelled()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Cancelled memberships cannot be extended");
        }

        if (membership.getEndDate().isBefore(LocalDate.now())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Expired memberships cannot be extended");
        }

        if (additionalMonths < 0 || additionalDays < 0 || (additionalMonths == 0 && additionalDays == 0)) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Extension duration must be positive");
        }

        if (billable && (request.price() == null || request.price() <= 0)) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Billable extensions require a positive price");
        }

        previousEndDate = membership.getEndDate();
        membership.extendBy(additionalMonths, additionalDays);
        membership = membershipRepository.save(membership);

        if (!billable) {
            return new ExtendMembershipResponse(
                    membership.getId().toString(),
                    membership.getStatus(),
                    previousEndDate,
                    membership.getEndDate(),
                    false,
                    null,
                    null,
                    null,
                    null,
                    "Membership extended"
            );
        }

        invoiceId = UUID.randomUUID().toString();
        invoiceDueDate = LocalDate.now().plusDays(30);
        now = Instant.now();

        var externalInvoice = restClient.post()
                .uri("/api/shared/external-invoice-provider/invoices")
                .contentType(MediaType.APPLICATION_JSON)
                .body(new ExternalInvoiceProviderUpsertRequest(
                        membership.getCustomerId(),
                        membership.getId().toString(),
                        request.price(),
                        "CHF",
                        invoiceDueDate,
                        ExternalInvoiceProviderStatus.OPEN,
                        "Membership extension invoice",
                        invoiceId,
                        Map.of(
                                "exercise", "membership",
                                "membershipId", membership.getId().toString(),
                                "extension", "true"
                        )
                ))
                .retrieve()
                .body(ExternalInvoiceProviderResponse.class);

        externalInvoiceId = externalInvoice == null ? invoiceId : externalInvoice.invoiceId();

        billingReference = billingReferenceRepository.save(new MembershipBillingReferenceEntity(
                UUID.randomUUID(),
                membership.getId(),
                externalInvoiceId,
                invoiceId,
                invoiceDueDate,
                "OPEN",
                now,
                now
        ));

        return new ExtendMembershipResponse(
                membership.getId().toString(),
                membership.getStatus(),
                previousEndDate,
                membership.getEndDate(),
                true,
                billingReference.getId().toString(),
                billingReference.getExternalInvoiceReference(),
                billingReference.getExternalInvoiceId(),
                billingReference.getDueDate(),
                "Membership extended and invoice created"
        );
    }

}
