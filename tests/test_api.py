from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sngpc.api.main import app
from sngpc.api.database import get_db
from sngpc.api.models import Base, Product
import pytest

from sqlalchemy.pool import StaticPool

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    # Seed data
    db = TestingSessionLocal()
    db.add(Product(numero_registro="100010001", nome_produto="TEST MED A", is_controlled=False))
    db.add(Product(numero_registro="100010002", nome_produto="TEST MED B", is_controlled=True, restriction_detail="Hospitalar"))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

def test_read_products():
    response = client.get("/products/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["nome_produto"] == "TEST MED A"

def test_search_products():
    response = client.get("/products/search?q=med b")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nome_produto"] == "TEST MED B"

def test_read_product_by_id():
    # First get list to find ID
    response = client.get("/products/search?q=med a")
    product_id = response.json()[0]["id"]
    
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["nome_produto"] == "TEST MED A"
