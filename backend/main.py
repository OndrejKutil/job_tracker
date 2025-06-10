from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers import application
from dotenv import load_dotenv
import os
from auth import verify_api_key

# Load environment variables from .env file
# This must be called before importing auth module
load_dotenv()

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
FRONTEND_URL = os.getenv("FRONTEND_URL")

# Create FastAPI app instance
app = FastAPI(
    title="Job Tracker API",
    description="A simple job tracking application",
)

# Add CORS middleware to allow frontend connections
if FRONTEND_URL:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
else:
    raise RuntimeError("FRONTEND_URL environment variable is not set.")

# Include routers
app.include_router(application.router, prefix="/application", tags=["application"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Job Tracker API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/version")
async def version(api_key: str = Depends(verify_api_key)):
    return {"version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
