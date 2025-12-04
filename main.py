from contextlib import asynccontextmanager
from typing import AsyncIterator, List

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import asc, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import SessionLocal, create_tables, get_db
from models import Recipe
from schemas import RecipeCreate, RecipeDetail, RecipeListItem, RecipeUpdate


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    print("Запуск приложения...")
    create_tables()
    await init_database()
    yield
    print("Завершение работы..")


async def init_database():
    print("Инициализация ...")

    db = SessionLocal()
    try:
        if db.query(Recipe).count() == 0:
            sample_recipes = [
                Recipe(
                    name="Спагетти Карбонара",
                    cooking_time=20,
                    ingredients=(
                        "Спагетти - 200г, Бекон - 150г, Яйца - 2 шт, "
                        "Сыр Пармезан - 50г, Чеснок - 2 зубчика, Соль, Перец"
                    ),
                    description=(
                        "Классическое итальянское блюдо с беконом и сырным соусом. "
                        "Приготовьте пасту аль денте, обжарьте бекон с чесноком, "
                        "смешайте с яйцами и сыром."
                    ),
                ),
                Recipe(
                    name="Шоколадный торт",
                    cooking_time=90,
                    ingredients=(
                        "Мука - 200г, Какао - 50г, Сахар - 200г, Яйца - 3 шт, "
                        "Сливочное масло - 150г, Разрыхлитель - 1 ч.л., Сметана - 100г"
                    ),
                    description=(
                        "Нежный шоколадный торт для настоящих сладкоежек. "
                        "Смешайте сухие ингредиенты, добавьте яйца и масло, "
                        "выпекайте 40 минут при 180°C."
                    ),
                ),
            ]
            db.add_all(sample_recipes)
            db.commit()
            print(f"Добавлено {len(sample_recipes)} рецептов")
        else:
            recipe_count = db.query(Recipe).count()
            print(f"В базе данных уже есть {recipe_count} рецептов")
    except SQLAlchemyError as e:
        print(f"Ошибка инициализации - {e}")
        db.rollback()
    finally:
        db.close()


app = FastAPI(
    title="cook API",
    description="API для кулинарной книги",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/docs",
    lifespan=lifespan,
)


@app.get("/", summary="Информация о API", tags=["Информация"])
async def root():
    return {
        "message": " Добро пожаловать",
        "docs": "/docs",
        "endpoints": {
            "get_recipes": "GET/recipes",
            "get_recipe": "GET/recipes/{id}",
            "create_recipe": "POST/recipes",
            "update_recipe": "PUT/recipes/{id}",
            "delete_recipe": "DELETE/recipes/{id}",
        },
    }


@app.get(
    "/recipes",
    response_model=List[RecipeListItem],
    summary="Получить список всех рецептов",
    description="""
    Возвращает список всех рецептов для отображения в таблице на первом экране.

    **Сортировка:**
    - По количеству просмотров (по убыванию) - чем популярнее рецепт, тем выше
    - По времени приготовления (по возрастанию) при равном количестве просмотров""",
    tags=["Рецепты"],
)
def get_recipes(db: Session = Depends(get_db)):
    try:
        recipes = (
            db.query(Recipe)
            .order_by(desc(Recipe.views), asc(Recipe.cooking_time))
            .all()
        )
        return recipes
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения данных - {str(e)}",
        )


@app.get(
    "/recipes/{recipe_id}",
    response_model=RecipeDetail,
    summary="Детали рецепта",
    tags=["Рецепты"],
)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(404, detail="Рецепт не найден")
    recipe.views += 1  # type: ignore
    db.commit()
    return recipe


@app.post(
    "/recipes",
    response_model=RecipeDetail,
    status_code=201,
    summary="Создать рецепт",
    tags=["Рецепты"],
)
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    new_recipe = Recipe(**recipe.model_dump())
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)
    return new_recipe


@app.put(
    "/recipes/{recipe_id}",
    response_model=RecipeDetail,
    summary="Обновить рецепт",
    description="""
    Обновляет существующий рецепт.
    Все поля опциональны - обновляются только переданные поля.
    """,
    tags=["Рецепты"],
)
def update_recipe(
    recipe_id: int, recipe_update: RecipeUpdate, db: Session = Depends(get_db)
):
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not db_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Рецепт с ID {recipe_id} не найден",
        )
    update_data = recipe_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_recipe, field, value)

    db.commit()
    db.refresh(db_recipe)

    return db_recipe


@app.delete(
    "/recipes/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить рецепт",
    description="Удаляет рецепт по ID.",
    tags=["Рецепты"],
)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not db_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Рецепт с ID {recipe_id} не найден",
        )

    db.delete(db_recipe)
    db.commit()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
