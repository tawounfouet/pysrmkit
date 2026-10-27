# PySRMKit — Pre-Implementation Specification Baseline

This directory contains the frozen pre-implementation baseline used to bootstrap PySRMKit.

## Core sequence

- `00_PYSRMKIT_EXPRESSION_DU_BESOIN.md`
- `01_PYSRMKIT_REQUIREMENTS_ANALYSIS.md`
- `02_PYSRMKIT_PRODUCT_VISION_AND_ARCHITECTURE_PRINCIPLES.md`
- `03_PYSRMKIT_SYSTEM_ARCHITECTURE.md`
- `04_PYSRMKIT_DOMAIN_OBJECTS.md`
- `05_PYSRMKIT_ENTITIES_AND_VALUE_OBJECTS.md`
- `06_PYSRMKIT_DOMAIN_RELATIONSHIPS_AND_ERD.md`
- `07_PYSRMKIT_DOMAIN_INVARIANTS_AND_BUSINESS_RULES.md`
- `08_PYSRMKIT_COMMANDS_QUERIES_AND_USE_CASES.md`
- `09_PYSRMKIT_DOMAIN_EVENTS_AND_EVENT_MODEL.md`
- `10_PYSRMKIT_PORTS_AND_REPOSITORY_CONTRACTS.md`
- `11_PYSRMKIT_REPOSITORY_AND_PACKAGE_ARCHITECTURE.md`
- `12_PYSRMKIT_TESTING_STRATEGY.md`
- `13_PYSRMKIT_IMPLEMENTATION_ROADMAP.md`
- `14_PYSRMKIT_IMPLEMENTATION_BOOTSTRAP_PLAN.md`

## Post-Core iterative reviews

The frozen baseline above is followed by targeted documents created only from implementation pressure.

- `15_PYSRMKIT_POST_CORE_ARCHITECTURE_REVIEW.md` - review of the qualified `0.1.0a1 -> 0.1.0a8` Core and Cycle 2 decision point.
- `16_PYSRMKIT_PERSISTENCE_ARCHITECTURE.md` - targeted persistence architecture for the `0.2.x` Persistent Core, including SQLAlchemy, SQLite, PostgreSQL, transaction and migration boundaries.

## Transverse conventions

- `PYSRMKIT_SOFTWARE_DESIGN_LEARNING_CONVENTION.md`
- `PYSRMKIT_PRE_IMPLEMENTATION_SPECIFICATION_CUTOFF_AND_ITERATIVE_DOCUMENTATION_STRATEGY.md`

General specification stopped after the bootstrap baseline. Documents numbered `15+` are iterative post-implementation deep dives and must be justified by real code, test, product, or infrastructure pressure.
