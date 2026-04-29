package com.workshop.architecture.fitness.application;

public class CustomerTooYoungException extends RuntimeException {

    public CustomerTooYoungException(String message) {
        super(message);
    }
}
