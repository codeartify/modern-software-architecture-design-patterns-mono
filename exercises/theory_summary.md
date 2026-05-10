# Modern Software Architecture — Internal Structure of Applications

## Participant Summary

This workshop focused on a central architectural question:

> How should we structure applications so they remain understandable, testable, and evolvable over time?

The focus was intentionally on the **internal structure of applications** — not infrastructure, deployment, or
distributed systems.

---

# Core Architectural Principles

## Architecture Is About Trade-Offs

Good architecture is not about applying one pattern everywhere.

The goal is to place boundaries where they:

* reduce coupling
* increase cohesion
* keep change local
* lower cognitive load
* make business rules easier to understand and evolve

A pattern is only useful if the benefits outweigh the added complexity.

---

## Coupling and Cohesion

Two of the most important concepts in architecture are:

### High Cohesion

Things that belong together should stay together.

Examples:

* business rules around memberships
* lifecycle decisions
* invariants protecting consistency

### Low Coupling

Things that change independently should be separated.

Examples:

* HTTP handling
* database access
* external APIs
* email sending

A large part of software architecture is balancing these two forces.

---

# Separating Concerns

The workshop distinguished three major concerns:

## Presentation (IN)

Responsible for user-/machine-facing entry points into a system:

* HTTP, APIs, KafkaListener, ...
* request/response mapping
* validation of incoming data

## Infrastructure / Gateways (OUT<->IN / OUT)

Responsible for communication with the outside world:

* repositories (bi-directional)

    * databases
    * external APIs, HTTP
    * file system
    * ...
* recipients (uni-directional)

    * messaging, KafkaTemplate, ...
    * email sending
    * notifications
    * ...

## Business Logic (CORE)

Responsible for providing the core functionality of the application:

* application business rules
* workflows
* core business rules and invariants / consistency
* lifecycle decisions

A major source of bad architecture is mixing these concerns together.

This is what often creates “spaghetti code.”

---

# Architecture Styles

## Layered Architecture

Separates applications into layers:

* Presentation
* Business:

    * Application
    * Domain
* Infrastructure

Access is top down:

* no layer below can access a layer above
* strict: every layer above may only access the layer directly below
* relaxed: a layer above may access any layer below

### Benefits

* easy to understand
* clear separation of concerns
* good starting point for many systems, especially simpler ones

### Trade-Offs

* everything depends on the infrastructure (data access) layer
* even the presentation concern may access it in case of relaxed layering
* features become scattered across layers
* application services can grow very large
* domain models often stay weak or anemic

---

## Onion Architecture

Onion Architecture can be seen as an evolution of layered architecture.

The key idea is:

> Dependencies point inward toward the business logic.

This is achieved through dependency inversion.

Typical structure:

* Domain (center)
* Application
* Presentation / Infrastructure (outside)

The core business logic no longer depends directly on infrastructure implementations.
Instead:

* repositories become interfaces/ports
* infrastructure provides implementations/adapters
* the domain and application layers stay independent from frameworks and databases

### Main Idea

Layered architecture with dependency inversion around infrastructure.

### Benefits

* business logic becomes independent from infrastructure
* improved testability
* clearer protection of the core model
* infrastructure becomes replaceable

### Trade-Offs

* more interfaces and indirection
* additional abstraction overhead
* can become unnecessary for simpler applications
* XYController, XYService, XY can become God Classes
* Layers can access everything within the same layer and below, possibly leading to a big ball of mud anyways

---

## Hexagonal Architecture / Ports & Adapters

Hexagonal Architecture focuses primarily on separating:

* the inside of the application
* from the outside world

The central distinction is:

* inside = business/application logic
* outside = frameworks, UI, databases, messaging, external systems

Communication happens through:

* ports (interfaces)
* adapters

Hexagonal Architecture intentionally says little about how the application should be structured internally.

It mainly defines:

> The application core should not depend on external technology.

### Benefits

* strong separation between business logic and external systems
* improved replaceability of infrastructure
* easier testing of application logic
* flexible integration models

### Trade-Offs

* additional indirection
* interface-heavy designs
* can lead to excessive abstraction if applied everywhere
* can still contain large god classes implementing many inbound ports

---

## Clean Architecture

Clean Architecture is an evolution of Hexagonal Architecture combining:

* dependency inversion and interface segregation
* explicit application boundaries
* use-case-oriented application structure
* core business rules in entities

A typical structure includes:

* Adapters (implement Outbound Ports):

    * Presentation:

        * Controllers
        * Presenters
    * Infrastructure:

        * Gateways
* Business:

    * Inbound Use Case Ports
    * Outbound Ports
    * Use Case Interactors (port implementations)
* Entities

### Main Concepts

#### Controllers

Handle incoming requests and translate them into use case input.

#### Gateways

Provide access to external systems:

* databases
* APIs
* messaging
* file systems

#### Use Case Ports

Define application use case interfaces.

#### Use Case Interactors

Implement application workflows and orchestration.

#### Entities

Contain enterprise/business rules.

This is often the place where a richer DDD-style domain model can live with:

* invariants
* lifecycle rules
* domain behavior
* consistency protection

### Main Idea

Protect the business rules and organize the application around explicit use cases.

### Benefits

* strong separation of concerns
* explicit application boundaries
* high testability
* good fit for complex business domains

### Trade-Offs

* significantly more indirection
* larger number of abstractions
* higher cognitive overhead
* can feel heavyweight for simpler systems

Key lesson:

> These architectures are useful when the additional boundaries and indirection provide real value.

---

## Vertical Slice Architecture

Structures applications by feature or use case.

Each slice typically contains:

* endpoint/controller
* request model
* handler
* persistence access
* business flow

### Benefits

* strong feature locality
* easier navigation
* lower cognitive load
* simpler evolutionary structure

### Trade-Offs

* some duplication may appear
* shared abstractions emerge later
* boundaries may initially be less explicit

Key insight:

> Vertical slices optimize for understanding and evolving features.

---

# Domain Modeling

A major theme of the workshop was the transition from:

* organizing code by technical structure

TO:

* identifying cohesive business models and invariants

## Rich vs Anemic Domain Models

### Anemic Model

Business logic mostly lives in services.

### Rich Domain Model

Behavior and rules live inside domain objects.

Examples:

* a membership decides whether it may reactivate
* a billing reference decides whether payment may be applied
* lifecycle rules become part of the model itself

---

# Domain-Driven Design (DDD)

The workshop emphasized that the main value of DDD is often:

* clearer business language
* lower coordination and change cost
* reduced overlap between parts of the system and better boundaries

Not every system needs deep domain modeling.

The level of structure should match the importance and complexity of the business logic.

---

# CQRS and Events

## CQRS

Separates:

* Commands (writes)
* Queries (reads)

Useful when:

* read and write models differ significantly
* reporting becomes complex
* performance requirements diverge

Usually unnecessary for simple CRUD systems.

---

## Domain Events

Events represent important things that happened in the domain.

Examples:

* MembershipActivated
* PaymentReceived
* MembershipSuspended

Events can help:

* decouple workflows
* model long-running processes
* introduce asynchronous boundaries

But they also introduce:

* eventual consistency
* retries
* idempotency concerns
* additional complexity

---

# Final Takeaways

* Architecture is about trade-offs, not patterns.
* Separate concerns before introducing advanced structure.
* Use layers, hexagonal boundaries, or vertical slices where they provide value.
* High cohesion and low coupling are core goals.
* Business rules and invariants should shape architecture.
* Not all code deserves the same level of rigor.

## Final Message

> Choose structure based on the kind of logic you are building - not based on patterns alone.
