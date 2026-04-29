package com.workshop.architecture.fitness.application.port.outbound;

public class CustomerNotFoundException extends RuntimeException {

    public CustomerNotFoundException(String message) {
        super(message);
    }

}
