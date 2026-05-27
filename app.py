from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from recipe_service import MODEL, generate_recipe

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

app = FastAPI(title="Ymeal Recipe API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RecipePredictionRequest(BaseModel):
    ingredient_search: str = ""
    ingredients_selected: List[str] = Field(default_factory=list)
    frigo: bool = False
    nombre_personne: int = Field(default=2, ge=1, le=20)
    difficulte: str = ""
    type_plat: str = ""
    temps_minutes: Optional[int] = Field(default=None, ge=1, le=300)
    contexte_personnel: str = ""
    regime: str = ""
    ingredients_interdits: List[str] = Field(default_factory=list)


class RecipePredictionResponse(BaseModel):
    recipe: str
    model: str


def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen = set()
    result: List[str] = []

    for raw_item in items:
        item = raw_item.strip()
        if not item:
            continue

        key = item.lower()
        if key in seen:
            continue

        seen.add(key)
        result.append(item)

    return result


def _extract_search_ingredients(value: str) -> List[str]:
    if not value.strip():
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/predict", response_model=RecipePredictionResponse)
@app.post("/api/predict/", response_model=RecipePredictionResponse)
def predict(payload: RecipePredictionRequest) -> RecipePredictionResponse:
    search_ingredients = _extract_search_ingredients(payload.ingredient_search)
    all_ingredients = _dedupe_keep_order(payload.ingredients_selected + search_ingredients)

    if not all_ingredients:
        raise HTTPException(status_code=400, detail="Ajoute au moins un ingredient.")

    try:
        recipe = generate_recipe(
            ingredients=all_ingredients,
            servings=payload.nombre_personne,
            personal_context=payload.contexte_personnel,
            diet=payload.regime,
            forbidden_ingredients=payload.ingredients_interdits,
            difficulty=payload.difficulte,
            dish_type=payload.type_plat,
            max_time_minutes=payload.temps_minutes,
            use_fridge=payload.frigo,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=502, detail=f"Erreur lors de la generation: {exc}") from exc

    return RecipePredictionResponse(recipe=recipe, model=MODEL)


@app.get("/", include_in_schema=False)
def serve_index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/styles.css", include_in_schema=False)
def serve_css() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "styles.css")


@app.get("/script.js", include_in_schema=False)
def serve_js() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "script.js")
