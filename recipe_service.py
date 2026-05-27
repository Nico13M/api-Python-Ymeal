import os
from typing import List, Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = os.getenv("OPENROUTER_MODEL", "google/gemma-4-31b-it:free")
# Exemple alternatif: MODEL = "google/gemma-3-27b-it:free"

_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY est manquante dans le fichier .env")

        _client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

    return _client


def build_prompt(
    ingredients: List[str],
    servings: int,
    personal_context: str = "",
    diet: str = "",
    forbidden_ingredients: Optional[List[str]] = None,
    difficulty: str = "",
    dish_type: str = "",
    max_time_minutes: Optional[int] = None,
    use_fridge: bool = False,
) -> str:
    forbidden_ingredients = forbidden_ingredients or []

    ingredients_str = ", ".join(ingredients) if ingredients else "Aucun ingredient fourni"
    forbidden_str = ", ".join(forbidden_ingredients) if forbidden_ingredients else "Aucun"
    diet_str = diet.strip() if diet else "Aucun"
    context_str = personal_context.strip() if personal_context else "Aucun"
    difficulty_str = difficulty.strip() if difficulty else "Aucune"
    dish_type_str = dish_type.strip() if dish_type else "Aucun"
    time_str = f"{max_time_minutes} minutes" if max_time_minutes else "Aucune"
    fridge_str = "Oui" if use_fridge else "Non"

    return f"""
Tu es un assistant cuisine.

Contraintes obligatoires :
- Regime alimentaire : {diet_str}
- Ingredients interdits (allergenes/exclusions) : {forbidden_str}
- Nombre de personnes : {servings}
- Contexte personnel utilisateur : {context_str}
- Niveau de difficulte souhaite : {difficulty_str}
- Type de plat souhaite : {dish_type_str}
- Temps max souhaite : {time_str}
- Ingredients deja dans le frigo : {fridge_str}
- Utilise en priorite les ingredients disponibles.
- N'utilise JAMAIS un ingredient interdit.
- Si le regime impose une contrainte (ex: vegetarien => pas de viande/poisson ; halal => pas de porc/alcool), respecte-la strictement.
- Si une contrainte rend la recette impossible avec les ingredients disponibles, propose une alternative faisable en expliquant quoi acheter.

Ingredients disponibles :
{ingredients_str}

Format de reponse (respecte exactement ces sections) :

### Recette
- Nom :
- Temps total :
- Niveau :
- Portions : {servings}

### Ingredients (quantites pour {servings} personnes)
- ...

### Etapes
1) ...
2) ...

### A acheter (si manquant, max 10 items)
- item - quantite

### Estimation prix (indicatif)
- ingredient - prix estime
- ...
- Total recette - prix estime

Important :
- Prix : donne une estimation simple en euros (fourchette ou valeur approximative), sans inventer de source.
- Verifie que rien n'enfreint le regime ni les interdits.
Reponds en francais.
""".strip()


def generate_recipe(
    ingredients: List[str],
    servings: int,
    personal_context: str = "",
    diet: str = "",
    forbidden_ingredients: Optional[List[str]] = None,
    difficulty: str = "",
    dish_type: str = "",
    max_time_minutes: Optional[int] = None,
    use_fridge: bool = False,
) -> str:
    if servings <= 0:
        raise ValueError("Le nombre de personnes (servings) doit etre > 0.")

    prompt = build_prompt(
        ingredients=ingredients,
        servings=servings,
        personal_context=personal_context,
        diet=diet,
        forbidden_ingredients=forbidden_ingredients,
        difficulty=difficulty,
        dish_type=dish_type,
        max_time_minutes=max_time_minutes,
        use_fridge=use_fridge,
    )

    client = _get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=900,
        temperature=0.7,
        extra_headers={
            "HTTP-Referer": "http://localhost",
            "X-Title": "Recettes - API",
        },
    )

    return response.choices[0].message.content or ""
