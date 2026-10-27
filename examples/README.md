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
