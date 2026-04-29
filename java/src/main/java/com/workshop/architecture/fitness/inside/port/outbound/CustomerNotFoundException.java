package com.workshop.architecture.fitness.inside.port.outbound;

public class CustomerNotFoundException extends RuntimeException {

    public CustomerNotFoundException(String message) {
        super(message);
    }

}
