package com.workshop.architecture.infrastructure;

public record ApiErrorResponse(
        int status,
        String error,
        String message,
        String path
) {
}
