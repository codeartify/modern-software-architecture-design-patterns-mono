package com.workshop.architecture.fitness.clean_architecture.use_case.port.outbound;

public class PlanNotFoundException extends RuntimeException {

    public PlanNotFoundException(String message) {
        super(message);
    }
}
