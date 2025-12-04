from sqlalchemy import Column, DateTime, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True, comment="Название блюда")
    cooking_time = Column(
        Integer, nullable=False, comment="Время приготовления в минутах"
    )
    ingredients = Column(Text, nullable=False, comment="Список ингредиентов")
    description = Column(Text, nullable=False, comment="Описание рецепта")
    views = Column(Integer, default=0, nullable=False, comment="Количество просмотров")
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
