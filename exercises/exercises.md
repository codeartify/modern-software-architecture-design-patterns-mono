# Exercises

## Mixed Architecture (main, snippets)
* Classify different snippets into the 3-4 concerns presentation, business (application, domain), and infrastructure / gateway.

* On branch: what does the code do?

## Layered Architecture (branch: exercise1 --> exercise1_solution)

1. Separate the classes into presentation, business (application, domain), and infrastructure / gateway concerns.
   * Move classes into the different folders

2. Move logic from the MembershipController::activateMembership to the MembershipService.
   * Ensure that dependencies only point from presentation -> business -> infrastructure, not the other way around.
      * MembershipService should not depend on MembershipController DTOs anymore

Simpler start: do the same for CustomerController::updateCustomer

## Hexagonal Architecture (branch: exercise1_solution --> exercise2_solution)

1. Add inbound and outbound ports and adapters to MembershipService::activateMembership
   * Think about what is outside and what is inside of the hexagon
   * Ensure the MembershipService does not depend on infrastructure classes anymore
   * Ensure the MembershipController doesn't directly depend on the MembershipService anymore
   * You need to adapt the external data to a minimal internal model and avoid exposing external data structures in port interfaces

Simpler start: create a hexagon for CustomerController::updateCustomer

## Clean Architecture (branch: exercise2_solution --> exercise3_solution)

1. Move the files from the hexagon's inside/outside folders into clean architectures folders
   * Adapters: Controller, Gateway, (Presenters)
   * Use Case & ports (inbound/outbound)
   * Entity
2. Find critical enterprise business rules and move it to the entities

Simpler start: create clean architecture for CustomerController::updateCustomer

## OPTIONAL: Richer Domain Model (branch: exercise3_solution --> exercise3b_solution)
1. add value objects for the different fields of Membership
2. Group fields that belong together into separate values.

==> Duration => can be derived from start and end date (no planDuration field required)


## Vertical Slice Architecture (branch: main --> exercise4_solution)

1. Start splitting up the MembershipController, PlanController, and CustomerController into multiple controllers (one
   for each public method), only keep what's required for that handler
2. Move shared classes to a shared folder
3. How can we avoid feature folder explosion?

Idea: Split first, then decide what to do in each slice individually. Refactor for shared concepts

## Bounded Contexts (exercise4_solution --> exercise5_solution)
1. Group the different use case folders by bounded contexts
2. Move generally shared concepts into higher level shared folders
   code do?
