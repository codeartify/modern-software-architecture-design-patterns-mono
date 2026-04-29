# Exercises

## Layered Architecture
1. Separate the concerns of MembershipController::activateMembership into presentation, business (application, domain), and infrastructure. 
   * Move classes into the different folders 
   * Move logic from the MembershipController to the MembershipService. 
   * Ensure that dependencies only point from presentation -> business -> infrastructure, not the other way around.


## Clean Architecture (branch: exercise2_solution)

1. Move the files from the hexagon's inside/outside folders into clean architectures folders
   * Adapters: Controller, Gateway, (Presenters)
   * Use Case & ports (inbound/outbound)
   * Entity
2. Split the MembershipService into multiple use case interactors with separate use case interfaces
3. Find critical enterprise business rules and move it to the entities
