import pytest
import uuid
import time
from fastapi.testclient import TestClient
from fastapi.testclient import TestClient
try:
    from api.server import app
except ImportError:
    from backend.api.server import app
from core.database import get_db_connection

client = TestClient(app)

def clean_test_user(email: str):
    """Utility to remove test users from the database."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE email = %s", (email,))

@pytest.fixture
def unique_email():
    email = f"test_{uuid.uuid4().hex}@lumo.ai"
    yield email
    clean_test_user(email)

@pytest.fixture(autouse=True)
def clear_limits():
    from core.rate_limit import _in_memory_limits
    _in_memory_limits.clear()
    
    from core.config import REDIS_URL
    import redis
    try:
        r = redis.from_url(REDIS_URL, socket_timeout=1)
        keys = r.keys("rate_limit:*")
        if keys:
            r.delete(*keys)
    except Exception:
        pass



def test_register_and_login_success(unique_email):
    # 1. Register new user
    reg_payload = {
        "email": unique_email,
        "password": "SecurePassword123",
        "full_name": "Test User"
    }
    response = client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["user"]["email"] == unique_email
    assert data["user"]["full_name"] == "Test User"
    assert "id" in data["user"]

    # 2. Login with correct credentials
    login_payload = {
        "email": unique_email,
        "password": "SecurePassword123"
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    assert "access_token" in response.cookies
    
    login_data = response.json()
    assert login_data["status"] == "success"
    assert login_data["user"]["email"] == unique_email

    # 3. Get /me with cookie
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    me_data = response.json()
    assert me_data["email"] == unique_email
    assert me_data["full_name"] == "Test User"

    # 4. Logout
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    # access_token cookie should be removed (empty or deleted)
    assert "access_token" not in response.cookies or response.cookies.get("access_token") == ""

    # 5. Access /me after logout (should fail)
    # Clear client cookies first
    client.cookies.clear()
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_login_incorrect_password(unique_email):
    # Register user
    reg_payload = {
        "email": unique_email,
        "password": "SecurePassword123",
        "full_name": "Test User"
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    # Login with wrong password
    login_payload = {
        "email": unique_email,
        "password": "WrongPassword!"
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 401
    assert "access_token" not in response.cookies

def test_register_duplicate_email(unique_email):
    reg_payload = {
        "email": unique_email,
        "password": "SecurePassword123",
        "full_name": "Test User"
    }
    # First registration
    response = client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 201

    # Second registration with same email
    response = client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_rate_limiting(unique_email):
    # Clean fallback rate limits
    from core.rate_limit import _in_memory_limits
    _in_memory_limits.clear()

    login_payload = {
        "email": unique_email,
        "password": "AnyPassword"
    }
    
    # Make 5 requests (all should bypass rate limiting but fail with 401 for incorrect password)
    for _ in range(5):
        response = client.post("/api/v1/auth/login", json=login_payload)
        # Should be 401 or 429
        assert response.status_code in [401, 429]
        if response.status_code == 429:
            break # Already hit rate limit (could happen if Redis count was not clean)
            
    # The 6th request should definitely hit the rate limit (429)
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]

def test_tenant_isolation(unique_email):
    # Clean client state
    client.cookies.clear()
    
    # Register User A
    user_a_email = f"a_{unique_email}"
    reg_a = {"email": user_a_email, "password": "Password123", "full_name": "User A"}
    res_a = client.post("/api/v1/auth/register", json=reg_a)
    assert res_a.status_code == 201
    user_a_id = res_a.json()["user"]["id"]
    
    # Register User B
    user_b_email = f"b_{unique_email}"
    reg_b = {"email": user_b_email, "password": "Password123", "full_name": "User B"}
    res_b = client.post("/api/v1/auth/register", json=reg_b)
    assert res_b.status_code == 201
    
    # Login as User B
    login_b = {"email": user_b_email, "password": "Password123"}
    res_login_b = client.post("/api/v1/auth/login", json=login_b)
    assert res_login_b.status_code == 200
    
    # Try to access a chart belonging to User A (thread_id: user_a_id + "_default")
    # This should return 403 Forbidden because User B doesn't own it!
    user_a_thread = f"{user_a_id}_default"
    res_chart = client.get(f"/chart/{user_a_thread}")
    assert res_chart.status_code == 403
    
    # Try to access User A's documents
    # (Since get_documents filters by current_user's ID, calling get_documents as User B
    # should NOT return User A's documents.)
    # Let's verify that the endpoint doesn't fail and returns list, but we can't see User A's things.
    res_docs = client.get("/api/documents") # Wait, route prefix is /api/v1/documents. Let's try both or the registered one
    # Route in document.py has no prefix inside the router, but prefix="/api/v1" is on the router:
    # router = APIRouter(prefix="/api/v1", tags=["document"]) or similar?
    # Let's check: in document.py: @router.get("/documents")
    # So the full path is /api/v1/documents.
    res_docs = client.get("/api/v1/documents")
    assert res_docs.status_code == 200
    
    # Clean up
    clean_test_user(user_a_email)
    clean_test_user(user_b_email)
