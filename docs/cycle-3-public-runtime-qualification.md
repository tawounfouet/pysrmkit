# Cycle 3 - Public Runtime Qualification

Version: `0.3.0a6`

This document records the executable qualification boundary that closes the
`0.3.x - Public API & Runtime Composition` architecture cycle.

## Consumer contract proved

The final consumer journey uses the public `pysrmkit.public` business surface to:

1. register a Supplier;
2. create and invite a Supplier Relationship;
3. start, satisfy, and complete onboarding;
4. create, answer, and complete an assessment;
5. request and evaluate qualification;
6. read immutable public Views;
7. observe the public qualification event.

The same journey is qualified for both:

- score 90 -> `QUALIFIED`;
- score 60 -> `NOT_QUALIFIED` with `ASSESSMENT_MINIMUM_SCORE`.

## Runtime matrix

| Runtime | Success | Rejection | Public Views | Events | Restart |
| --- | --- | --- | --- | --- | --- |
| InMemory | yes | yes | yes | yes | n/a |
| SQLite | yes | yes | yes | yes | yes |
| PostgreSQL | yes | yes | yes | yes | persistence contracts already qualified |

SQLite restart qualification explicitly destroys the first Engine/runtime and
constructs a fresh Engine/runtime against the same database before reloading the
public Supplier and Qualification views.

## Architecture properties retained

- the public facade contains no business rule duplication;
- consumers construct no Repository or SQLAlchemy Session;
- SQL operations retain operation-scoped transactions;
- onboarding retains its capability UnitOfWork;
- public SQL events are delivered after commit;
- failed commits publish no success event;
- public reads return immutable Views, never ORM records;
- persistence failures are translated at the public boundary;
- migrations/schema lifecycle remain explicit and are not hidden in runtime startup;
- Domain, Application, and Ports are prevented by architecture fitness tests from
  importing the Public Runtime layer.

## Design concepts actually exercised

- **Facade** - `PySRMKit` simplifies access to capability subsystems.
- **Composition Root** - runtime factories select adapters and wire dependencies.
- **Primary Adapter** - capability APIs drive Application use cases.
- **Ports and Adapters** - persistence remains behind repository ports.
- **CQRS-lite** - commands reuse application results while reads map to immutable Views.
- **Observer / Publish-Subscribe** - typed public Domain Event subscriptions.
- **Transaction Boundary** - one ordinary SQL command owns one short-lived transaction.
- **Unit of Work** - onboarding preserves its multi-repository atomic boundary.
- **Dependency Inversion** - Core layers do not depend on Runtime or SQL infrastructure.
- **Information Hiding** - repository/session/ORM details stay outside the consumer contract.

## Cycle 3 exit gate

The qualified Supplier Core is consumable through a small typed Python API while
preserving Domain semantics, transaction ownership, durable persistence, public
read models, stable errors, and event ordering.
