"""Tests for the 0.3.0a4 public Python API foundation."""

from pysrmkit import PySRMKit, RelationshipsAPI, SuppliersAPI
from pysrmkit.adapters.memory.relationship_repository import InMemorySupplierRelationshipRepository
from pysrmkit.adapters.memory.supplier_repository import InMemorySupplierRepository
from pysrmkit.application.relationship.commands import CreateSupplierRelationship
from pysrmkit.application.relationship.results import CreateSupplierRelationshipResult
from pysrmkit.application.supplier.commands import RegisterSupplier
from pysrmkit.application.supplier.results import RegisterSupplierResult
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId
from pysrmkit.domain.supplier.value_objects import SupplierId
from pysrmkit.public.query_handlers import (
    GetSupplierHandler,
    GetSupplierRelationshipHandler,
    ListSuppliersHandler,
)


class RegisterSupplierSpy:
    """Records the public API command while returning a deterministic result."""

    def __init__(self, result: RegisterSupplierResult) -> None:
        self.command: RegisterSupplier | None = None
        self._result = result

    def handle(self, command: RegisterSupplier, /) -> RegisterSupplierResult:
        self.command = command
        return self._result


class CreateRelationshipSpy:
    """Records relationship creation without requiring runtime composition."""

    def __init__(self, result: CreateSupplierRelationshipResult) -> None:
        self.command: CreateSupplierRelationship | None = None
        self._result = result

    def handle(
        self,
        command: CreateSupplierRelationship,
        /,
    ) -> CreateSupplierRelationshipResult:
        self.command = command
        return self._result


def test_suppliers_api_translates_primitives_to_register_command() -> None:
    expected = RegisterSupplierResult(supplier_id=SupplierId.new())
    handler = RegisterSupplierSpy(expected)
    api = SuppliersAPI(
        register_supplier=handler,
        get_supplier=GetSupplierHandler(InMemorySupplierRepository()),
        list_suppliers=ListSuppliersHandler(InMemorySupplierRepository()),
    )

    result = api.register(
        legal_name=" ACME SAS ",
        trading_name="ACME",
        country_code="FR",
    )

    assert result is expected
    assert handler.command == RegisterSupplier(
        legal_name=" ACME SAS ",
        trading_name="ACME",
        country_code="FR",
    )


def test_relationships_api_builds_internal_organization_id() -> None:
    supplier_id = SupplierId.new()
    expected = CreateSupplierRelationshipResult(relationship_id=SupplierRelationshipId.new())
    handler = CreateRelationshipSpy(expected)

    class NoOpHandler:
        def handle(self, command: object, /) -> None:
            del command

    api = RelationshipsAPI(
        create_relationship=handler,
        invite_relationship=NoOpHandler(),
        start_onboarding=NoOpHandler(),
        get_relationship=GetSupplierRelationshipHandler(InMemorySupplierRelationshipRepository()),
    )

    result = api.create(
        supplier_id=supplier_id,
        organization_id=" FR-BU ",
    )

    assert result is expected
    assert handler.command is not None
    assert handler.command.supplier_id == supplier_id
    assert handler.command.organization_id.value == "FR-BU"


def test_facade_exposes_capabilities_without_runtime_magic() -> None:
    supplier_result = RegisterSupplierResult(supplier_id=SupplierId.new())
    suppliers = SuppliersAPI(
        register_supplier=RegisterSupplierSpy(supplier_result),
        get_supplier=GetSupplierHandler(InMemorySupplierRepository()),
        list_suppliers=ListSuppliersHandler(InMemorySupplierRepository()),
    )

    assert "in_memory" in PySRMKit.__dict__
    assert "sql" in PySRMKit.__dict__
    assert suppliers.register(legal_name="ACME") is supplier_result
