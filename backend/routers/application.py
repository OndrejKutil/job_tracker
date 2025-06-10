from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

import supabase
import os
from dotenv import load_dotenv

from auth import verify_api_key


# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("PROJECT_URL")
DATABASE_KEY = os.getenv("ANON_KEY")

# Create Supabase client
supabase_client = supabase.create_client(DATABASE_URL, DATABASE_KEY)

# Create a new FastAPI router for application-related endpoints
router = APIRouter()


class ApplicationStatus(str, Enum):
    """Valid status values for job applications"""
    INTERESTED = "interested"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    REJECTED = "rejected"
    ACCEPTED = "accepted"

# ApplicationCreate model for creating new applications
class ApplicationCreate(BaseModel):
    """Model for creating new applications - excludes auto-generated fields"""
    user_id: str
    company_name: Optional[str] = None
    recruiter: Optional[str] = None
    job_title: Optional[str] = None
    job_url: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    applied_date: Optional[date] = None  
    notes: Optional[str] = None

# Application model for responses - includes all fields
class Application(BaseModel):
    """Model for application responses - includes all fields"""
    application_id: str
    user_id: str
    company_name: Optional[str] = None
    recruiter: Optional[str] = None
    job_title: Optional[str] = None
    job_url: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    applied_date: Optional[date] = None 
    notes: Optional[str] = None
    created_at: Optional[datetime] = None 
    updated_at: Optional[datetime] = None




@router.get("/all", response_model=List[Application])
async def get_all_applications(api_key: str = Depends(verify_api_key)):
    """Get all applications - requires API key authentication"""
    try:
        response = supabase_client.table('applications').select('*').execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching applications: {str(e)}")

@router.get("/{application_uuid}", response_model=Application)
async def get_application(application_uuid: str, api_key: str = Depends(verify_api_key)):
    """Get a specific application by UUID - requires API key authentication"""
    try:
        response = supabase_client.table('applications').select('*').eq('application_id', application_uuid).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Application not found")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching application: {str(e)}")

@router.get("/user/{user_id}", response_model=List[Application])
async def get_user_applications(user_id: str, api_key: str = Depends(verify_api_key)):
    """Get all applications for a specific user - requires API key authentication"""
    try:
        response = supabase_client.table('applications').select('*').eq('user_id', user_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching applications: {str(e)}")

@router.post("/", response_model=Application)
async def create_application(application: ApplicationCreate, api_key: str = Depends(verify_api_key)):
    """Create a new application - requires API key authentication"""
    try:
        # Convert to dict and exclude None values for cleaner insert
        data = application.dict(exclude_none=True)
        
        # Convert date to string format for JSON serialization
        if 'applied_date' in data and data['applied_date'] is not None:
            data['applied_date'] = data['applied_date'].isoformat()
        
        response = supabase_client.table('applications').insert(data).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating application: {str(e)}")
    

@router.put("/{application_uuid}", response_model=Application)
async def update_application(application_uuid: str, application: ApplicationCreate, api_key: str = Depends(verify_api_key)):
    """Update an existing application - requires API key authentication"""
    try:
        # Convert to dict and exclude None values for cleaner update
        data = application.dict(exclude_none=True)
        
        # Convert date to string format for JSON serialization
        if 'applied_date' in data and data['applied_date'] is not None:
            data['applied_date'] = data['applied_date'].isoformat()
        
        response = supabase_client.table('applications').update(data).eq('application_id', application_uuid).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Application not found")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating application: {str(e)}")
    

@router.delete("/{application_uuid}", response_model=dict)
async def delete_application(application_uuid: str, api_key: str = Depends(verify_api_key)):
    """Delete an application by UUID - requires API key authentication"""
    try:
        response = supabase_client.table('applications').delete().eq('application_id', application_uuid).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Application not found")
        
        return {"message": "Application deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting application: {str(e)}")
    

@router.delete("/user/{user_id}", response_model=dict)
async def delete_user_applications(user_id: str, api_key: str = Depends(verify_api_key)):
    """Delete all applications for a specific user - requires API key authentication"""
    try:
        response = supabase_client.table('applications').delete().eq('user_id', user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="No applications found for this user")
        
        return {"message": "All applications for user deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user applications: {str(e)}")

