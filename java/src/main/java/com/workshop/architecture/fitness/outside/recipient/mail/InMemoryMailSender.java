package com.workshop.architecture.fitness.outside.recipient.mail;

import com.workshop.architecture.fitness.inside.port.outbound.CustomerActivateMembershipEmail;
import com.workshop.architecture.fitness.inside.port.outbound.ForSendingEmails;
import com.workshop.architecture.fitness.infrastructure.InMemoryEmailService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class InMemoryMailSender implements ForSendingEmails {

    private final InMemoryEmailService emailService;
    private final String billingSenderEmailAddress;

    public InMemoryMailSender(InMemoryEmailService emailService,
                              @Value("${workshop.billing.sender-email-address}") String billingSenderEmailAddress) {
        this.emailService = emailService;
        this.billingSenderEmailAddress = billingSenderEmailAddress;
    }

    @Override
    public void sendEmail(CustomerActivateMembershipEmail emailDetails) {
        var activationEmail = emailDetails.emailTemplate().formatted(
                        emailDetails.emailAddress(),
                        billingSenderEmailAddress,
                        emailDetails.invoiceId(),
                        emailDetails.invoiceId(),
                        emailDetails.planPrice(),
                        emailDetails.invoiceDueDate(),
                        emailDetails.invoiceId()
                )
                .replace("\n|", "\n")
                .trim();

        System.out.println(activationEmail);

        emailService.send(activationEmail);
    }
}
