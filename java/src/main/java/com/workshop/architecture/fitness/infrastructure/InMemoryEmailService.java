package com.workshop.architecture.fitness.infrastructure;

import java.util.ArrayList;
import java.util.List;
import org.springframework.stereotype.Component;

@Component
public class InMemoryEmailService {

    private final List<String> sentEmails = new ArrayList<>();

    public void send(String emailContent) {
        sentEmails.add(emailContent);
    }

    public List<String> sentEmails() {
        return List.copyOf(sentEmails);
    }

    public void clear() {
        sentEmails.clear();
    }
}
