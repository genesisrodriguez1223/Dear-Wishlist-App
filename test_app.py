
import sqlite3
import pytest
import app as wishlist


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Use a temporary database instead of the real one
    monkeypatch.chdir(tmp_path)
    wishlist.init_db()
    wishlist.app.config["TESTING"] = True

    with wishlist.app.test_client() as client:
        yield client


# Test 1: Homepage loads
def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Dear Wishlist" in response.data


# Test 2: User can add a wishlist item
def test_add_item(client):
    response = client.post("/add", data={
        "name": "Pink Backpack",
        "price": "35.99",
        "store": "Target",
        "priority": "High"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Pink Backpack" in response.data


# Test 3: Item information saves correctly
def test_item_saved_correctly(client):
    client.post("/add", data={
        "name": "Pink Backpack",
        "price": "35.99",
        "store": "Target",
        "priority": "High"
    })

    conn = sqlite3.connect("wishlist.db")
    item = conn.execute(
        "SELECT name, price, store, priority FROM items"
    ).fetchone()
    conn.close()

    assert item == ("Pink Backpack", 35.99, "Target", "High")


# Test 4: New wishlist database starts empty
def test_empty_database(client):
    conn = sqlite3.connect("wishlist.db")
    count = conn.execute(
        "SELECT COUNT(*) FROM items"
    ).fetchone()[0]
    conn.close()

    assert count == 0
def test_valid_priority():
    assert wishlist.valid_priority("High") is True
    assert wishlist.valid_priority("Medium") is True
    assert wishlist.valid_priority("Low") is True


def test_invalid_priority():
    assert wishlist.valid_priority("Urgent") is False
    assert wishlist.valid_priority("") is False


def test_reject_invalid_priority(client):
    response = client.post("/add", data={
        "name": "Pink Backpack",
        "price": "35.99",
        "store": "Target",
        "priority": "Urgent"
    })

    assert response.status_code == 400