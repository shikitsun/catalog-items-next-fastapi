import pytest
from app.core.config import get_settings

ADMIN = {"x-admin-token": get_settings().internal_token}

@pytest.mark.asyncio
async def test_create_item(client):
    response = await client.post(
        "/items", data={"title": "Item 1"}, files={
                "file": (
                    "test.jpg",
                    b"test",
                    "image/jpeg",
                )
            }, headers=ADMIN
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Item 1"
    assert "id" in body
    assert body["preview_url"].startswith("http")


@pytest.mark.asyncio
async def test_list_items_empty(client):
    response = await client.get("/items/all")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_then_get(client):
    create = await client.post(
        "/items", data={"title": "Item 2"}, files={
                "file": (
                    "test.jpg",
                    b"test",
                    "image/jpeg",
                )
            }, headers=ADMIN
    )
    item_id = create.json()["id"]

    fetch = await client.get(f"/items/{item_id}")
    assert fetch.status_code == 200
    assert fetch.json()["title"] == "Item 2"


@pytest.mark.asyncio
async def test_update_item(client):
    create = await client.post("/items", data={"title": "Initial"}, headers=ADMIN)
    item_id = create.json()["id"]

    update = await client.patch(f"/items/{item_id}", json={"title": "Updated"}, headers=ADMIN)
    assert update.status_code == 200
    assert update.json()["title"] == "Updated"


@pytest.mark.asyncio
async def test_create_requires_admin_token(client):
    response = await client.post("/items", data={"title": "Item 3"}, files={
                "file": (
                    "test.jpg",
                    b"test",
                    "image/jpeg",
                )
            })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_nonexistent_returns_404(client):
    response = await client.get("/items/99999999")
    assert response.status_code == 404