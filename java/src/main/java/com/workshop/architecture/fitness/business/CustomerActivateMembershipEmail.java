package com.workshop.architecture.fitness.business;

import java.time.LocalDate;

public record CustomerActivateMembershipEmail(String invoiceId, LocalDate invoiceDueDate, String emailAddress,
                                              int planPrice, String emailTemplate) {
}
