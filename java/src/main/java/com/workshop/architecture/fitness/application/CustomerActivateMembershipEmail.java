package com.workshop.architecture.fitness.application;

import java.time.LocalDate;

public record CustomerActivateMembershipEmail(String invoiceId, LocalDate invoiceDueDate, String emailAddress,
                                              int planPrice, String emailTemplate) {
}
