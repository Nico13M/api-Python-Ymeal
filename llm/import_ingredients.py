import argparse
import os
import sys
import math
from datetime import datetime, timezone
from pathlib import Path
 
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
 
DEFAULT_CSV = Path(__file__).parent.parent /"data" / "openfoodfacts_clean.csv"
 
load_dotenv()
 
INSERT_SQL = text("""
    INSERT INTO public.ingredient (
        name, slug, code_off,
        generic_name, categories_tags, allergens, nutriscore_grade, image_small_url,
        energy_100g, fat_100g, "saturated-fat_100g",
        carbohydrates_100g, sugars_100g, fiber_100g, proteins_100g, salt_100g,
        created_at, updated_at
    ) VALUES (
        :name, :slug, :code_off,
        :generic_name, :categories_tags, :allergens, :nutriscore_grade, :image_small_url,
        :energy_100g, :fat_100g, :saturated_fat_100g,
        :carbohydrates_100g, :sugars_100g, :fiber_100g, :proteins_100g, :salt_100g,
        :created_at, :updated_at
    )
    ON CONFLICT (slug) DO UPDATE SET
        name               = EXCLUDED.name,
        code_off           = EXCLUDED.code_off,
        generic_name       = EXCLUDED.generic_name,
        categories_tags    = EXCLUDED.categories_tags,
        allergens          = EXCLUDED.allergens,
        nutriscore_grade   = EXCLUDED.nutriscore_grade,
        image_small_url    = EXCLUDED.image_small_url,
        energy_100g        = EXCLUDED.energy_100g,
        fat_100g           = EXCLUDED.fat_100g,
        "saturated-fat_100g" = EXCLUDED."saturated-fat_100g",
        carbohydrates_100g = EXCLUDED.carbohydrates_100g,
        sugars_100g        = EXCLUDED.sugars_100g,
        fiber_100g         = EXCLUDED.fiber_100g,
        proteins_100g      = EXCLUDED.proteins_100g,
        salt_100g          = EXCLUDED.salt_100g,
        updated_at         = EXCLUDED.updated_at
""")
 
 
# =========================
# CLEANING ROBUSTE TYPES
# =========================
def clean_value(v):
    # NaN pandas / numpy
    if v is None:
        return None
 
    if isinstance(v, float) and math.isnan(v):
        return None
 
    # Timestamp pandas → datetime python
    if isinstance(v, pd.Timestamp):
        return v.to_pydatetime()
 
    # Tronquer les chaines trop longues pour VARCHAR(255)
    if isinstance(v, str) and len(v) > 255:
        return v[:255]
 
    return v
 
 
def clean_row(row: dict) -> dict:
    return {k: clean_value(v) for k, v in row.items()}
 
 
# =========================
def get_engine():
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        sys.exit("Erreur : variable d'environnement DATABASE_URL manquante.")
 
    url = url.replace("postgres://", "postgresql://", 1)
 
    if "+psycopg" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
 
    return create_engine(url)
 
 
# =========================
def import_csv(csv_path: Path, dry_run: bool = False) -> None:
    if not csv_path.exists():
        sys.exit(f"Erreur : fichier introuvable → {csv_path}")
 
    df = pd.read_csv(csv_path, dtype={"code": str}, low_memory=False)
 
    # rename colonnes
    if "code" in df.columns:
        df = df.rename(columns={"code": "code_off"})
 
    if "product_name" in df.columns:
        df = df.rename(columns={"product_name": "name"})
 
    # mapping colonne SQL
    if "saturated-fat_100g" in df.columns:
        df = df.rename(columns={"saturated-fat_100g": "saturated_fat_100g"})
 
    # slug
    if "slug" not in df.columns:
        df["slug"] = df["name"]
 
    mask = df["slug"].isna() | (df["slug"].astype(str).str.strip() == "")
    df.loc[mask, "slug"] = df.loc[mask, "name"]
 
    df["slug"] = (
        df["slug"]
        .astype(str)
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "-", regex=True)
        .str.strip("-")
    )
 
    # timestamps → Python datetime natif (IMPORTANT)
    now = datetime.now(timezone.utc)
    df["created_at"] = now
    df["updated_at"] = now
 
    print(f"{len(df)} ligne(s) à importer.")
 
    if dry_run:
        print("\n-- DRY RUN --")
        print(df.head(10))
        return
 
    success = 0
    errors = 0
 
    engine = get_engine()
    for r in df.to_dict(orient="records"):
 
        r = clean_row(r)
 
        try:
            with engine.begin() as conn:
                conn.execute(INSERT_SQL, r)
            success += 1

        except Exception as exc:
            errors += 1
            print(f"❌ Erreur sur '{r.get('name', 'inconnu')}' : {exc}")
 
    print(f"\nTerminé : {success} OK, {errors} erreurs")
 
 
# =========================
def main():
    parser = argparse.ArgumentParser(description="Importe des ingrédients depuis un CSV.")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
 
    import_csv(args.csv, dry_run=args.dry_run)
 
 
if __name__ == "__main__":
    main()