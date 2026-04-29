package com.workshop.architecture.fitness.application.port.outbound;

import com.workshop.architecture.fitness.application.CustomerActivateMembershipEmail;

public interface ForSendingEmails {
    void sendEmail(CustomerActivateMembershipEmail email);
}
