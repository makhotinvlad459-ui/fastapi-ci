import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# flake8: noqa: E402
from fastapi.testclient import TestClient
from database import Base, engine
from main import app

Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_read_root():
    """Тест корневого эндпоинта"""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    # Проверяем структуру ответа, а не конкретные значения
    assert "message" in data
    assert "docs" in data
    assert "endpoints" in data
    # Проверяем что message не пустой
    assert len(data["message"]) > 0


def test_get_recipes_not_empty():
    """Тест получения списка рецептов (база уже содержит данные)"""
    response = client.get("/recipes")
    assert response.status_code == 200

    data = response.json()
    # Проверяем что получаем список
    assert isinstance(data, list)
    # Проверяем структуру каждого рецепта в списке
    if len(data) > 0:
        recipe = data[0]
        assert "id" in recipe
        assert "name" in recipe
        assert "cooking_time" in recipe
        assert "views" in recipe


def test_create_recipe():
    """Тест создания рецепта"""
    recipe_data = {
        "name": "Тестовый рецепт",
        "cooking_time": 30,
        "ingredients": "тестовые ингредиенты",
        "description": "тестовое описание",
    }

    response = client.post("/recipes", json=recipe_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Тестовый рецепт"
    assert data["cooking_time"] == 30
    assert "id" in data
    assert "created_at" in data


def test_get_recipe_by_id():
    """Тест получения конкретного рецепта по ID"""
    # Создаем рецепт
    recipe_data = {
        "name": "Рецепт для деталей",
        "cooking_time": 40,
        "ingredients": "ингредиенты",
        "description": "описание",
    }
    create_response = client.post("/recipes", json=recipe_data)
    recipe_id = create_response.json()["id"]

    # Получаем его по ID
    response = client.get(f"/recipes/{recipe_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == recipe_id
    assert data["name"] == "Рецепт для деталей"
    assert data["views"] == 1


def test_create_recipe_validation_error():
    """Тест ошибки валидации при создании"""
    invalid_data = {
        "name": "",  # пустое название
        "cooking_time": 0,  # нулевое время
        "ingredients": "",
        "description": "",
    }

    response = client.post("/recipes", json=invalid_data)
    assert response.status_code == 422
