from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


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


# TODO В данном проекте намного удобнее использовать две таблицы, соединённые с помощью поля "внешний ключ": Receipt и
#  Ingredient. В таблице Ingredient храним ингредиенты рецептов, одна запись - один ингредиент, состав полей модели
#  примерно такой:
#  - внешний ключ на таблицу Рецепт
#  - название ингредиента
#  - количество ингредиента
#  - единица измерения
#  - примечание (описание)
#  Можно добавить ещё полей по желанию. А вот дублировать "время приготовления"
