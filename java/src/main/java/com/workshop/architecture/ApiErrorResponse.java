package com.workshop.architecture;

public record ApiErrorResponse(
        int status,
        String error,
        String message,
        String path
) {
}
