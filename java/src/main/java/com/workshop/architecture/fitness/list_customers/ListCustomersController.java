package com.workshop.architecture.fitness.list_customers;

import com.workshop.architecture.fitness.shared.CustomerEntity;
import com.workshop.architecture.fitness.shared.CustomerRepository;
import com.workshop.architecture.fitness.shared.CustomerResponse;
import java.util.Comparator;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/customers")
public class ListCustomersController {

    private final CustomerRepository customerRepository;

    public ListCustomersController(CustomerRepository customerRepository) {
        this.customerRepository = customerRepository;
    }

    @GetMapping
    List<CustomerResponse> listCustomers() {
        return customerRepository.findAll().stream()
                .sorted(Comparator.comparing(CustomerEntity::getName))
                .map(CustomerResponse::fromEntity)
                .toList();
    }
}
