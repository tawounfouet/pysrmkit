# PySRMKit Examples

## Local Core qualification

The first executable end-to-end Core scenario is:

```bash
python examples/local_qualification.py
```

It manually assembles the local composition root:

```text
InMemorySupplierRepository
InMemorySupplierRelationshipRepository
InMemorySupplierOnboardingRepository
InMemorySupplierAssessmentRepository
InMemorySupplierQualificationRepository
FixedClock
InProcessDomainEventDispatcher
QualificationPolicy
Application Handlers
```

No dependency-injection container, database, network service, broker, or framework runtime is required.

The scenario performs:

```text
RegisterSupplier
CreateSupplierRelationship
InviteSupplierRelationship
StartSupplierOnboarding
SatisfyOnboardingRequirement
CompleteSupplierOnboarding
CreateSupplierAssessment
RecordAssessmentAnswer
CompleteSupplierAssessment
RequestSupplierQualification
EvaluateSupplierQualification
```

The explicit onboarding completion steps refine the original roadmap sequence because the implemented QualificationPolicy now consumes `onboarding_complete` as a real prerequisite.

The default example produces a final `QUALIFIED` SupplierQualification and prints the observed Domain Event trace.


## Persistent Core qualification

The second executable end-to-end scenario is:

```bash
python examples/persistent_qualification.py
```

It reuses the same Domain and Application model but substitutes real SQL infrastructure:

```text
Alembic schema bootstrap
SQLAlchemy Engine / Session
SqlAlchemySupplierRepository
SqlAlchemySupplierRelationshipRepository
SqlAlchemySupplierOnboardingRepository
SqlAlchemySupplierAssessmentRepository
SqlAlchemySupplierQualificationRepository
SqlAlchemySupplierOnboardingUnitOfWork
DeferredDomainEventDispatcher
QualificationPolicy
Application Handlers
```

The default demonstration uses a disposable SQLite file. Qualification tests execute the same persistent journey against PostgreSQL 18.

The scenario deliberately proves a restart boundary:

```text
execute business journey
        ↓
commit durable state
        ↓
destroy original Engine / Session / Repositories
        ↓
create fresh persistence context
        ↓
reload all Aggregates
        ↓
same qualification outcome
```

Both `QUALIFIED` and `NOT_QUALIFIED` paths are qualified.
