package com.workshop.architecture;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.Map;

import com.workshop.architecture.config.HealthController;
import org.junit.jupiter.api.Test;

class ApplicationTests {

    @Test
    void healthEndpointReturnsOkStatus() {
        HealthController controller = new HealthController();

        assertThat(controller.health()).isEqualTo(Map.of("status", "ok"));
    }
}
