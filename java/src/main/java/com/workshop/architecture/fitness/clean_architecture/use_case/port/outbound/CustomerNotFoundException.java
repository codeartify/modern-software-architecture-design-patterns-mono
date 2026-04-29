package com.workshop.architecture.fitness.clean_architecture.use_case.port.outbound;

public class CustomerNotFoundException extends RuntimeException {

    public CustomerNotFoundException(String message) {
        super(message);
    }

}
