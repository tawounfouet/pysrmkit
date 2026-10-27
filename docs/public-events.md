# Public Domain Events - 0.3.0a5

PySRMKit exposes a deliberately small synchronous Domain Event subscription surface:

```python
from pysrmkit import PySRMKit, SupplierQualified

srm = PySRMKit.in_memory()
srm.events.subscribe(SupplierQualified, handler)
```

## Delivery contract

Public event delivery is:

- in-process;
- synchronous;
- typed by exact event class;
- ordered according to publication within the current process;
- post-commit for SQL-backed business operations.

The SQL runtime buffers events produced inside ordinary transactions and publishes them only after the database commit succeeds. A failed commit discards buffered events. The onboarding capability keeps its existing UnitOfWork semantics, which already dispatch after its explicit commit.

## Durability boundary

The public event surface is intentionally **non-durable**.

It does not promise:

- replay;
- crash recovery;
- at-least-once delivery;
- exactly-once delivery;
- broker delivery;
- cross-process delivery;
- a transactional outbox.

Consumers requiring durable integration should treat this API as a local observation/integration hook until a future Outbox or external messaging capability is explicitly designed.

## Compatibility

Only events intentionally exported from `pysrmkit` / `pysrmkit.public` are public compatibility contracts. Internal Domain Events are not automatically public.

For a promoted event, its name, fields, field meanings, and documented delivery timing are compatibility-sensitive.
