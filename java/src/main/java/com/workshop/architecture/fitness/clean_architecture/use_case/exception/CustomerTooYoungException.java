package com.workshop.architecture.fitness.clean_architecture.use_case.exception;

public class CustomerTooYoungException extends RuntimeException {

    public CustomerTooYoungException(String message) {
        super(message);
    }
}
