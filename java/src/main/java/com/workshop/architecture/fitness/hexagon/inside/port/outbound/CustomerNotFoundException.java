package com.workshop.architecture.fitness.hexagon.inside.port.outbound;

public class CustomerNotFoundException extends RuntimeException {

    public CustomerNotFoundException(String message) {
        super(message);
    }

}
