package com.workshop.architecture.fitness.inside.port.outbound;

public interface ForSendingEmails {
    void sendEmail(CustomerActivateMembershipEmail email);
}
