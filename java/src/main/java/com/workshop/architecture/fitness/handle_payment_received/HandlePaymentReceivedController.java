package com.workshop.architecture.fitness.handle_payment_received;

import com.workshop.architecture.fitness.shared.MembershipBillingReferenceEntity;
import com.workshop.architecture.fitness.shared.MembershipBillingReferenceRepository;
import com.workshop.architecture.fitness.shared.MembershipEntity;
import com.workshop.architecture.fitness.shared.MembershipRepository;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import java.time.Instant;
import java.time.ZoneOffset;
import java.util.UUID;

@RestController
@RequestMapping("/api/memberships")
public class HandlePaymentReceivedController {

    private final MembershipRepository membershipRepository;
    private final MembershipBillingReferenceRepository billingReferenceRepository;

    public HandlePaymentReceivedController(
            MembershipRepository membershipRepository,
            MembershipBillingReferenceRepository billingReferenceRepository
    ) {
        this.membershipRepository = membershipRepository;
        this.billingReferenceRepository = billingReferenceRepository;
    }


    @PostMapping("/payment-received")
    ResponseEntity<PaymentReceivedResponse> paymentReceived(@RequestBody PaymentReceivedRequest request) {
        MembershipBillingReferenceEntity billingReference;
        MembershipEntity membership;
        Instant paidAt;
        String previousMembershipStatus;
        String newMembershipStatus;
        String message;
        boolean reactivated;

        if ((request.externalInvoiceId() == null || request.externalInvoiceId().isBlank())
                && (request.externalInvoiceReference() == null || request.externalInvoiceReference().isBlank())
                && (request.membershipId() == null || request.membershipId().isBlank())) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "At least one invoice or membership identifier must be provided"
            );
        }

        if (request.externalInvoiceId() != null && !request.externalInvoiceId().isBlank()) {
            billingReference = billingReferenceRepository.findByExternalInvoiceId(request.externalInvoiceId())
                    .orElse(null);
        } else {
            billingReference = null;
        }

        if (billingReference == null
                && request.externalInvoiceReference() != null
                && !request.externalInvoiceReference().isBlank()) {
            billingReference = billingReferenceRepository.findByExternalInvoiceReference(
                    request.externalInvoiceReference()
            ).orElse(null);
        }

        if (billingReference == null && request.membershipId() != null && !request.membershipId().isBlank()) {
            billingReference = billingReferenceRepository.findByMembershipId(UUID.fromString(request.membershipId()))
                    .stream()
                    .findFirst()
                    .orElse(null);
        }

        if (billingReference == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "No billing reference was found");
        }

        paidAt = request.paidAt() == null ? Instant.now() : request.paidAt();
        message = billingReference.isPaid()
                ? "Payment was already recorded; membership status unchanged"
                : "Payment recorded; membership status unchanged";

        if (!billingReference.isPaid()) {
            billingReference.markPaid(paidAt);
            billingReference = billingReferenceRepository.save(billingReference);
        }

        UUID billingReferenceMembershipId = billingReference.getMembershipId();

        membership = membershipRepository.findById(billingReferenceMembershipId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Membership %s was not found".formatted(billingReferenceMembershipId)
                ));

        previousMembershipStatus = membership.getStatus();
        newMembershipStatus = membership.getStatus();
        reactivated = false;

        if (membership.isCancelled()) {
            message = "Payment recorded; membership is cancelled and remains unchanged";
        } else if (membership.isSuspendedForNonPayment()) {
            if (!paidAt.atZone(ZoneOffset.UTC).toLocalDate().isAfter(membership.getEndDate())) {
                membership.reactivateAfterPayment();
                membership = membershipRepository.save(membership);
                newMembershipStatus = membership.getStatus();
                message = "Payment recorded; membership reactivated";
                reactivated = true;
            }
        }

        return ResponseEntity.ok(new PaymentReceivedResponse(
                paidAt,
                membership.getId().toString(),
                billingReference.getId().toString(),
                previousMembershipStatus,
                newMembershipStatus,
                reactivated,
                message
        ));
    }
}
