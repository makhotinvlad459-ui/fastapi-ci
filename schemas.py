from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RecipeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Название блюда")
    cooking_time: int = Field(..., gt=0, description="Время приготовления в минутах")
    ingredients: str = Field(..., min_length=1, description="Список ингредиентов")
    description: str = Field(..., min_length=1, description="Описание рецепта")


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(BaseModel):
    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Название блюда"
    )
    cooking_time: Optional[int] = Field(
        None, gt=0, description="Время приготовления в минутах"
    )
    ingredients: Optional[str] = Field(
        None, min_length=1, description="Список ингредиентов"
    )
    description: Optional[str] = Field(
        None, min_length=1, description="Текстовое описание рецепта"
    )


class RecipeListItem(BaseModel):
    id: int = Field(..., description="номер рецепта")
    name: str = Field(..., description="Название блюда")
    cooking_time: int = Field(..., description="Время приготовления в минутах")
    views: int = Field(..., description="Количество просмотров")

    class Config:
        from_attributes = True


class RecipeDetail(RecipeListItem):
    ingredients: str = Field(..., description="Список ингредиентов")
    description: str = Field(..., description="Текстовое описание рецепта")
    created_at: datetime = Field(..., description="Дата и время создания")
    updated_at: datetime = Field(..., description="Дата и время последнего обновления")

    class Config:
        from_attributes = True
