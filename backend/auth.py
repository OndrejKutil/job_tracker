"""
Authentication module for Job Tracker API

This module provides simple API key authentication for protecting endpoints.
It's designed to be beginner-friendly with detailed explanations.

How it works:
1. API key is stored in .env file
2. Frontend sends the key in request headers
3. This module validates the key before allowing access to endpoints
4. If key is missing or wrong, returns 401 Unauthorized error
"""

import os
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Load environment variables
# os.getenv() reads values from .env file (when using python-dotenv)
# If API_KEY is not found in .env, it defaults to None
API_KEY = os.getenv("API_KEY")

# Security scheme for FastAPI
# HTTPBearer means we expect "Bearer <token>" in Authorization header
# auto_error=False means we handle errors manually instead of automatic 401
security = HTTPBearer(auto_error=False)

def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    """
    Dependency function that verifies the API key from request headers.
    
    This function is called automatically by FastAPI when you add it as a dependency
    to your endpoint functions using Depends().
    
    How it works:
    1. FastAPI automatically extracts the Authorization header
    2. HTTPBearer expects format: "Authorization: Bearer your_api_key_here"
    3. credentials.credentials contains just the key part (without "Bearer ")
    4. We compare it with our stored API_KEY from .env
    5. If valid, function returns successfully
    6. If invalid, raises HTTPException with 401 status
    
    Args:
        credentials: Automatically injected by FastAPI from Authorization header
        
    Returns:
        str: The validated API key
        
    Raises:
        HTTPException: 401 Unauthorized if key is missing or invalid
    """
    
    # Check if API_KEY was loaded from .env file
    if not API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key not configured on server"
        )
    
    # Check if Authorization header was provided
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Please provide 'Authorization: Bearer your_api_key' header"
        )
    
    # Check if the provided API key matches our stored key
    if credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # If we reach here, the API key is valid
    return credentials.credentials

def get_current_api_key() -> str:
    """
    Simple function to get the configured API key.
    Useful for testing or administrative purposes.
    
    Returns:
        str: The configured API key from environment
    """
    return API_KEY or "Not configured"
