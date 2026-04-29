package com.workshop.architecture.fitness.inside.port.outbound;

public class PlanNotFoundException extends RuntimeException {

    public PlanNotFoundException(String message) {
        super(message);
    }
}
