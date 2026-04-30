package com.workshop.architecture.config;

public record ApiErrorResponse(
        int status,
        String error,
        String message,
        String path
) {
}
