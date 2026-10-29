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


## FastAPI canonical Supplier search (Cycle 4 A4-02)

The optional FastAPI example exposes two intentionally different
read surfaces:

- `GET /suppliers?query=...`: unchanged **legacy** search that also
  considers supplier type, country and external identifiers, in UUID
  listing order. Existing Next.js consumers continue to use it.
- `GET /suppliers/search`: new **opt-in canonical** name search that
  delegates to `srm.suppliers.search()`, with explicit country/type filters
  and deterministic legal-name ordering.

Examples:

```bash
curl 'http://localhost:8000/suppliers/search?query=atlas&country_code=FR&supplier_type=MANUFACTURER&sort_order=asc&offset=0&limit=25'
curl 'http://localhost:8000/suppliers?query=ERP-654&offset=0&limit=25'
```

The canonical route returns the same Supplier page JSON shape as the legacy
route, including `items`, filtered `total`, `offset` and `limit`.
It defaults to `limit=25` at the HTTP boundary and maps invalid inputs
to HTTP 422. It does **not** search external identifiers or Supplier Type
as text. See
[`27_PYSRMKIT_CANONICAL_HTTP_SUPPLIER_SEARCH_CONTRACT.md`](../docs/specifications/27_PYSRMKIT_CANONICAL_HTTP_SUPPLIER_SEARCH_CONTRACT.md).

No dashboard migration, package version change or new mandatory Core
dependency is implied by the example host.
