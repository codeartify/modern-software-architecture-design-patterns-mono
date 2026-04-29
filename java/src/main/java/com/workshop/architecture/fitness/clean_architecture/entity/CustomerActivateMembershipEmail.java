package com.workshop.architecture.fitness.clean_architecture.entity;

import java.time.LocalDate;

public record CustomerActivateMembershipEmail(String invoiceId, LocalDate invoiceDueDate, String emailAddress,
                                              int planPrice, String emailTemplate) {
}
