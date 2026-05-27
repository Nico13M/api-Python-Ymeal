# Database Schema Documentation

Generated from the SQLAlchemy inspection query on `ymeal_bdd_3642` (schema `public`).

## Summary

- Database: `ymeal_bdd_3642`
- Main schema: `public`
- Tables: `13`
- Columns: `61`
- Foreign keys: `17`

## Tables

### `public.user`

| Column | Type | Nullable |
|---|---|---|
| id | INTEGER | NO |
| firstname | VARCHAR(45) | NO |
| lastname | VARCHAR(45) | NO |
| email | VARCHAR(255) | NO |
| password_hash | VARCHAR(255) | NO |
| created_at | TIMESTAMP | NO |
| updated_at | TIMESTAMP | NO |

### `public.subscription`

| Column | Type | Nullable |
|---|---|---|
| id | INTEGER | NO |
| name | VARCHAR(255) | NO |
| price | INTEGER | YES |
| duration_months | INTEGER | YES |

### `public.user_subscription`

| Column | Type | Nullable |
|---|---|---|
| id | INTEGER | NO |
| start_date | DATE | NO |
| end_date | DATE | NO |
| is_active | BOOLEAN | YES |
| user_id_id | INTEGER | YES |
| subscription_id_id | INTEGER | YES |

### `public.diet`

| Column | Type | Nullable |
|---|---|---|
| id | INTEGER | NO |
| name | VARCHAR(45) | NO |

### `public.diet_user`

| Column | Type | Nullable |
|---|---|---|
| diet_id | INTEGER | NO |
| user_id | INTEGER | NO |

### `public.units`

| Column | Type | Nullable |
|---|---|---|
| id | INTEGER | NO |
| name | VARCHAR(45) | NO |
| symbol | VARCHAR(45) | YES |

### `public.ingredient`

| Column | Type | Nullable |
|---|---|---|
| id | INTEGER | NO |
| name | VARCHAR(255) | NO |
| slug | VARCHAR(255) | NO |
| created_at | TIMESTAMP | NO |
| updated_at | TIMESTAMP | NO |
| units_id | INTEGER | YES |
| code_off | INTEGER | NO |
| generic_name | VARCHAR(255) | YES |
| categories_tags | VARCHAR(255) | YES |
| allergens | VARCHAR(255) | YES |
| nutriscore_grade | VARCHAR(255) | YES |
| image_small_url | VARCHAR(255) | YES |
| energy_100g | NUMERIC | YES |
| fat_100g | NUMERIC | YES |
| saturated-fat_100g | NUMERIC | YES |
| carbohydrates_100g | NUMERIC | YES |
| sugars_100g | NUMERIC | YES |
| fiber_100g | NUMERIC | YES |
| proteins_100g | NUMERIC | YES |
| salt_100g | NUMERIC | YES |

### `public.recipe`

| Column | Type | Nullable |
|---|---|---|
| id | INTEGER | NO |
| name | VARCHAR(255) | NO |
| slug | VARCHAR(255) | NO |
| description | TEXT | NO |
| image | VARCHAR(255) | YES |
| servings | INTEGER | NO |
| duration | INTEGER | YES |
| time | INTEGER | YES |
| difficulty | VARCHAR(50) | YES |
| dish_type | VARCHAR(100) | YES |
| is_public | BOOLEAN | NO |
| created_at | TIMESTAMP | NO |
| updated_at | TIMESTAMP | NO |
| user_id | INTEGER | NO |

### `public.recipe_ingredient`

| Column | Type | Nullable |
|---|---|---|
| id | INTEGER | NO |
| quantity | INTEGER | NO |
| unit | VARCHAR(20) | YES |
| recipe_id | INTEGER | NO |
| ingredient_id | INTEGER | NO |

### `public.recipe_diet`

| Column | Type | Nullable |
|---|---|---|
| recipe_id | INTEGER | NO |
| diet_id | INTEGER | NO |

### `public.user_recipe`

| Column | Type | Nullable |
|---|---|---|
| user_id | INTEGER | NO |
| recipe_id | INTEGER | NO |

### `public.frigo`

| Column | Type | Nullable |
|---|---|---|
| id | INTEGER | NO |
| user_frigo_id | INTEGER | YES |

### `public.frigo_ingredient`

| Column | Type | Nullable |
|---|---|---|
| frigo_id | INTEGER | NO |
| ingredient_id | INTEGER | NO |

### `public.user_ingredient`

| Column | Type | Nullable |
|---|---|---|
| user_id | INTEGER | NO |
| ingredient_id | INTEGER | NO |

## Foreign Keys

- `public.diet_user.diet_id` -> `public.diet.id`
- `public.diet_user.user_id` -> `public.user.id`
- `public.frigo.user_frigo_id` -> `public.user.id`
- `public.frigo_ingredient.frigo_id` -> `public.frigo.id`
- `public.frigo_ingredient.ingredient_id` -> `public.ingredient.id`
- `public.ingredient.units_id` -> `public.units.id`
- `public.recipe.user_id` -> `public.user.id`
- `public.recipe_diet.diet_id` -> `public.diet.id`
- `public.recipe_diet.recipe_id` -> `public.recipe.id`
- `public.recipe_ingredient.ingredient_id` -> `public.ingredient.id`
- `public.recipe_ingredient.recipe_id` -> `public.recipe.id`
- `public.user_ingredient.ingredient_id` -> `public.ingredient.id`
- `public.user_ingredient.user_id` -> `public.user.id`
- `public.user_recipe.recipe_id` -> `public.recipe.id`
- `public.user_recipe.user_id` -> `public.user.id`
- `public.user_subscription.subscription_id_id` -> `public.subscription.id`
- `public.user_subscription.user_id_id` -> `public.user.id`

## Re-run Inspection

```bash
cd llm
python db_schema_inspect.py
```
