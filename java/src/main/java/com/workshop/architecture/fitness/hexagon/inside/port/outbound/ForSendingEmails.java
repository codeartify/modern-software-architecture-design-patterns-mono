package com.workshop.architecture.fitness.hexagon.inside.port.outbound;

public interface ForSendingEmails {
    void sendEmail(CustomerActivateMembershipEmail email);
}
