"""Automated and idempotent PostgreSQL provisioning, Alembic migration, and seeding."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import psycopg
from alembic import command
from alembic.config import Config
from psycopg import sql
from sqlalchemy.engine import make_url

from examples.seed_suppliers import seed_suppliers
from pysrmkit import PySRMKit
from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine

DEFAULT_PYSRMKIT_DB_URL = "postgresql+psycopg://postgres@localhost:5432/pysrmkit"
DEFAULT_NEXT_DASHBOARD_DB_URL = "postgres://postgres@localhost:5432/next_dashboard"


def ensure_database_exists(db_url: str, admin_db: str = "postgres") -> bool:
    """Ensure target PostgreSQL database exists. Return True if created, False if existed."""
    parsed = make_url(db_url)
    target_db = parsed.database
    if not target_db:
        raise ValueError(f"No database name specified in URL: {db_url}")

    host = parsed.host or "localhost"
    port = parsed.port or 5432
    user = parsed.username or "postgres"

    admin_conninfo = f"host={host} port={port} user={user} dbname={admin_db}"
    if parsed.password:
        admin_conninfo += f" password={parsed.password}"

    with psycopg.connect(admin_conninfo, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (target_db,))
            if cur.fetchone() is not None:
                return False

            cur.execute(
                sql.SQL("CREATE DATABASE {} OWNER {};").format(
                    sql.Identifier(target_db),
                    sql.Identifier(user),
                )
            )
            return True


def run_alembic_migrations(db_url: str, config_path: Path | None = None) -> None:
    """Run Alembic migrations to the latest revision."""
    if config_path is None:
        config_path = Path(__file__).resolve().parent.parent / "alembic.ini"
    cfg = Config(str(config_path))
    cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(cfg, "head")


def seed_pysrmkit_suppliers(db_url: str) -> tuple[int, int]:
    """Register demonstration suppliers into PySRMKit. Return (created, skipped)."""
    engine = create_persistence_engine(db_url)
    try:
        return seed_suppliers(PySRMKit.sql(engine))
    finally:
        engine.dispose()


def seed_nextjs_dashboard(
    dashboard_dir: Path | None = None,
    postgres_url: str | None = None,
) -> bool:
    """Run the Next.js database seed script if the dashboard directory exists."""
    if dashboard_dir is None:
        env_dir = os.getenv("NEXTJS_DASHBOARD_DIR")
        if env_dir:
            dashboard_dir = Path(env_dir)
        else:
            dashboard_dir = (
                Path(__file__).resolve().parent.parent.parent
                / "resources"
                / "nextjs-acme-dashboard"
            )

    if not dashboard_dir.is_dir() or not (dashboard_dir / "scripts" / "seed.js").exists():
        return False

    env = os.environ.copy()
    if postgres_url:
        env["POSTGRES_URL"] = postgres_url

    subprocess.run(
        ["node", "-r", "dotenv/config", "./scripts/seed.js"],
        cwd=str(dashboard_dir),
        env=env,
        check=True,
    )
    return True


def bootstrap(
    pysrmkit_db_url: str | None = None,
    nextjs_db_url: str | None = None,
    seed_nextjs: bool = True,
) -> dict[str, object]:
    """Execute the full bootstrap sequence: databases, migrations, and seeds."""
    pysrmkit_url = pysrmkit_db_url or os.getenv("PYSRMKIT_DATABASE_URL", DEFAULT_PYSRMKIT_DB_URL)
    nextjs_url = nextjs_db_url or os.getenv("POSTGRES_URL", DEFAULT_NEXT_DASHBOARD_DB_URL)

    # 1. Provision databases
    pysrmkit_created = ensure_database_exists(pysrmkit_url)
    nextjs_created = ensure_database_exists(nextjs_url)

    # 2. Run Alembic migrations
    run_alembic_migrations(pysrmkit_url)

    # 3. Seed PySRMKit demo suppliers
    created_suppliers, skipped_suppliers = seed_pysrmkit_suppliers(pysrmkit_url)

    # 4. Optionally seed Next.js dashboard
    nextjs_seeded = False
    if seed_nextjs:
        nextjs_seeded = seed_nextjs_dashboard(postgres_url=nextjs_url)

    return {
        "pysrmkit_db_created": pysrmkit_created,
        "nextjs_db_created": nextjs_created,
        "suppliers_created": created_suppliers,
        "suppliers_skipped": skipped_suppliers,
        "nextjs_seeded": nextjs_seeded,
    }


def main() -> None:
    print("[1/4] Ensuring PostgreSQL databases exist...")
    result = bootstrap()

    pysrmkit_status = "created" if result["pysrmkit_db_created"] else "already exists"
    nextjs_status = "created" if result["nextjs_db_created"] else "already exists"
    print(f"      - pysrmkit: {pysrmkit_status}")
    print(f"      - next_dashboard: {nextjs_status}")

    print("[2/4] Alembic migrations: UP TO DATE")

    print(
        f"[3/4] Demo suppliers: {result['suppliers_created']} created, "
        f"{result['suppliers_skipped']} skipped"
    )

    if result["nextjs_seeded"]:
        print("[4/4] Next.js Acme Dashboard: SEEDED")
    else:
        print("[4/4] Next.js Acme Dashboard: SKIPPED (directory not found)")

    print("\nEnvironment bootstrap complete.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Bootstrap failed: {exc}", file=sys.stderr)
        sys.exit(1)
