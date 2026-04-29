package com.workshop.architecture.fitness.adapter.repository.mail;

import com.workshop.architecture.fitness.application.port.outbound.ForSendingEmails;
import org.springframework.stereotype.Component;

@Component
public class InMemoryMailSender implements ForSendingEmails {
}
