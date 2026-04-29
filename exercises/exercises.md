# Exercises

## Layered Architecture
1. Separate the concerns of MembershipController::activateMembership into presentation, business (application, domain), and infrastructure. 
   * Move classes into the different folders 
   * Move logic from the MembershipController to the MembershipService. 
   * Ensure that dependencies only point from presentation -> business -> infrastructure, not the other way around.


