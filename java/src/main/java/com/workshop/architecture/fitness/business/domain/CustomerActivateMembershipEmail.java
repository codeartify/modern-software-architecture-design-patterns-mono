package com.workshop.architecture.fitness.business.domain;

import java.time.LocalDate;

public record CustomerActivateMembershipEmail(String invoiceId, LocalDate invoiceDueDate, String emailAddress,
                                              int planPrice, String emailTemplate) {
}
