package com.workshop.architecture.fitness.business;

public class CustomerTooYoungException extends RuntimeException {

    public CustomerTooYoungException(String message) {
        super(message);
    }
}
