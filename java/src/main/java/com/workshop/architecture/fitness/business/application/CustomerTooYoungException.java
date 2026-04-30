package com.workshop.architecture.fitness.business.application;

public class CustomerTooYoungException extends RuntimeException {

    public CustomerTooYoungException(String message) {
        super(message);
    }
}
