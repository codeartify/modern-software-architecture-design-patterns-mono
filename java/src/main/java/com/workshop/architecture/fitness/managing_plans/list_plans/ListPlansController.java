package com.workshop.architecture.fitness.managing_plans.list_plans;

import com.workshop.architecture.fitness.managing_plans.shared.PlanEntity;
import com.workshop.architecture.fitness.managing_plans.shared.PlanRepository;
import com.workshop.architecture.fitness.managing_plans.shared.PlanResponse;
import java.util.Comparator;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/plans")
public class ListPlansController {

    private final PlanRepository planRepository;

    public ListPlansController(PlanRepository planRepository) {
        this.planRepository = planRepository;
    }

    @GetMapping
    List<PlanResponse> listPlans() {
        return planRepository.findAll().stream()
                .sorted(Comparator.comparing(PlanEntity::getTitle))
                .map(PlanResponse::fromEntity)
                .toList();
    }
}
