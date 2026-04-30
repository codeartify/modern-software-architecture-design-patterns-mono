package com.workshop.architecture.fitness.clean_architecture.entity;

import java.time.LocalDate;
import java.time.Period;

public record Duration(LocalDate startDate, LocalDate endDate) {

    public int inMonths() {
        return (int) Period.between(startDate, endDate).toTotalMonths();
    }
}
