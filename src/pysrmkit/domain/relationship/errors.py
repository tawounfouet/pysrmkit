"""Domain errors raised by SupplierRelationship lifecycle rules."""

from pysrmkit.domain.relationship.value_objects import SupplierLifecycleStage


class InvalidLifecycleTransition(ValueError):
    """Raised when a SupplierRelationship lifecycle transition is forbidden."""

    def __init__(
        self,
        *,
        source: SupplierLifecycleStage,
        target: SupplierLifecycleStage,
    ) -> None:
        self.source = source
        self.target = target
        super().__init__(f"Cannot transition SupplierRelationship from {source} to {target}")
