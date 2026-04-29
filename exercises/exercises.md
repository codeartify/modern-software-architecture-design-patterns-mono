# Exercises

## Layered Architecture
1. Move the classes of the membership into the different folders presentation, business (application, domain), and infrastructure.
2. Move logic from the MembershipController to the MembershipService. 
   * Ensure that dependencies only point from presentation -> business -> infrastructure, not the other way around.
