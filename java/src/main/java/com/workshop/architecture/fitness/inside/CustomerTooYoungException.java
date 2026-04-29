package com.workshop.architecture.fitness.inside;

public class CustomerTooYoungException extends RuntimeException {

    public CustomerTooYoungException(String message) {
        super(message);
    }
}
