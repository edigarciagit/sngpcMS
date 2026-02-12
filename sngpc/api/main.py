from fastapi import FastAPI
from .database import engine, Base
from .routers import products

# Create tables if they don't exist (though loader does this, it's good practice)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SNGPC Microservice API",
    description="API for accessing Anvisa SNGPC medication data",
    version="1.0.0"
)

app.include_router(products.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
