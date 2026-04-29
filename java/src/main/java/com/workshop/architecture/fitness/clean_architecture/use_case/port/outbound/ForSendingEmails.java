package com.workshop.architecture.fitness.clean_architecture.use_case.port.outbound;

import com.workshop.architecture.fitness.clean_architecture.entity.CustomerActivateMembershipEmail;

public interface ForSendingEmails {
    void sendEmail(CustomerActivateMembershipEmail email);
}
