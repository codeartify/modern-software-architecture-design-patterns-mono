package com.workshop.architecture.fitness.application.port.outbound;

public class PlanNotFoundException extends RuntimeException {

    public PlanNotFoundException(String message) {
        super(message);
    }
}
