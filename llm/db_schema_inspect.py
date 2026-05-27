import os
from pathlib import Path
from typing import Iterable, List

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text


def normalize_database_url(raw_url: str) -> str:
    url = raw_url.strip()
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    # Force psycopg driver because psycopg is available in this project env.
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)

    return url


def print_columns_for_schema(engine, schema: str) -> None:
    inspector = inspect(engine)
    tables = inspector.get_table_names(schema=schema)

    if not tables:
        print(f"\n[{schema}] (no tables)")
        return

    print(f"\n[{schema}]")
    for table in tables:
        print(f"  - {table}")
        columns = inspector.get_columns(table, schema=schema)
        for col in columns:
            nullable = "NULL" if col.get("nullable", True) else "NOT NULL"
            print(f"      - {col['name']} :: {col.get('type')} ({nullable})")


def fetch_user_schemas(engine) -> List[str]:
    inspector = inspect(engine)
    excluded = {"pg_catalog", "information_schema", "pg_toast"}
    return [schema for schema in inspector.get_schema_names() if schema not in excluded]


def print_foreign_keys(engine, schemas: Iterable[str]) -> None:
    schema_tuple = tuple(schemas)
    if not schema_tuple:
        print("\n=== Foreign Keys ===")
        print("No user schemas found.")
        return

    placeholders = ", ".join(f":s{i}" for i in range(len(schema_tuple)))
    params = {f"s{i}": schema for i, schema in enumerate(schema_tuple)}

    fk_sql = text(
        f"""
        SELECT
          tc.table_schema,
          tc.table_name,
          kcu.column_name,
          ccu.table_name AS foreign_table_name,
          ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
         AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema IN ({placeholders})
        ORDER BY tc.table_schema, tc.table_name, kcu.column_name;
        """
    )

    with engine.connect() as conn:
        rows = conn.execute(fk_sql, params).fetchall()

    print("\n=== Foreign Keys ===")
    print(f"Found: {len(rows)}")
    for schema, table, column, foreign_table, foreign_column in rows:
        print(f"- {schema}.{table}.{column} -> {schema}.{foreign_table}.{foreign_column}")


def main() -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(dotenv_path=env_path)

    raw_url = os.getenv("DATABASE_URL", "").strip()
    if not raw_url:
        raise SystemExit("DATABASE_URL manquante dans .env")

    engine = create_engine(normalize_database_url(raw_url), pool_pre_ping=True)

    with engine.connect() as conn:
        db_name = conn.execute(text("SELECT current_database()")).scalar_one()
        current_schema = conn.execute(text("SELECT current_schema()")).scalar_one()
        print(f"Connected to database: {db_name}")
        print(f"Current schema: {current_schema}")

    schemas = fetch_user_schemas(engine)
    print("\n=== Schemas / Tables / Columns ===")
    if not schemas:
        print("No user schemas found.")
    for schema in schemas:
        print_columns_for_schema(engine, schema)

    print_foreign_keys(engine, schemas)


if __name__ == "__main__":
    main()
