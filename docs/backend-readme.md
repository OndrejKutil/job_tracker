# 🔧 Backend Documentation - FastAPI Implementation

## 📋 Overview

The backend is built with **FastAPI**, a modern, high-performance Python web framework. It provides a clean RESTful API with automatic documentation, robust data validation, and security features.

## 🏗️ Architecture

### **Project Structure**
```
backend/
├── main.py                 # Application entry point & FastAPI configuration
├── auth.py                 # Authentication middleware & security
└── routers/
    └── application.py      # Application CRUD endpoints
```

### **Core Components**

#### **main.py - Application Entry Point**
- **FastAPI Application Instance**: Configured with title, description, and metadata
- **CORS Middleware**: Enables cross-origin requests from the frontend
- **Router Integration**: Modular endpoint organization
- **Environment Configuration**: Loads configuration from environment variables

```python
app = FastAPI(
    title="Job Tracker API",
    description="A simple job tracking application",
)

# CORS configuration for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

#### **auth.py - Security Layer**
- **API Key Authentication**: Simple but effective security mechanism
- **Bearer Token Support**: Industry-standard authorization header format
- **Dependency Injection**: FastAPI's dependency system for reusable auth
- **Error Handling**: Meaningful HTTP error responses

**Key Features:**
- Validates `Authorization: Bearer <token>` headers
- Returns proper HTTP status codes (401, 500)
- Detailed error messages for debugging
- Environment variable configuration

```python
def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Dependency function that verifies API key from request headers"""
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    if not credentials or credentials.credentials != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
```

#### **routers/application.py - Business Logic**
- **CRUD Operations**: Complete Create, Read, Update, Delete functionality
- **Data Validation**: Pydantic models for request/response serialization
- **Database Integration**: Supabase client for PostgreSQL operations
- **Error Handling**: Comprehensive exception management

## 📊 Data Models

### **ApplicationCreate Model**
Used for creating new applications and updates:
```python
class ApplicationCreate(BaseModel):
    user_id: str
    company_name: Optional[str] = None
    recruiter: Optional[str] = None
    job_title: Optional[str] = None
    job_url: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    applied_date: Optional[date] = None
    notes: Optional[str] = None
```

### **Application Model**
Complete application data including auto-generated fields:
```python
class Application(BaseModel):
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
```

### **ApplicationStatus Enum**
Controlled vocabulary for application statuses:
```python
class ApplicationStatus(str, Enum):
    INTERESTED = "interested"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
```

## 🔌 API Endpoints

### **Public Endpoints**
- `GET /` - Welcome message
- `GET /health` - Health check for monitoring

### **Authenticated Endpoints**
All require `Authorization: Bearer <api_key>` header:

#### **Application Management**
- `GET /application/all` - Retrieve all applications (admin)
- `GET /application/{application_uuid}` - Get specific application
- `GET /application/user/{user_id}` - Get user's applications
- `POST /application/` - Create new application
- `PUT /application/{application_uuid}` - Update application
- `DELETE /application/{application_uuid}` - Delete application
- `DELETE /application/user/{user_id}` - Bulk delete user applications

#### **System Information**
- `GET /version` - API version information

## 🗄️ Database Integration

### **Supabase Connection**
```python
# Environment-based configuration
DATABASE_URL = os.getenv("PROJECT_URL")
DATABASE_KEY = os.getenv("ANON_KEY")

# Client initialization
supabase_client = supabase.create_client(DATABASE_URL, DATABASE_KEY)
```

### **Database Operations**

#### **Create Operation**
```python
@router.post("/", response_model=Application)
async def create_application(application: ApplicationCreate, api_key: str = Depends(verify_api_key)):
    try:
        data = application.dict(exclude_none=True)
        if 'applied_date' in data and data['applied_date'] is not None:
            data['applied_date'] = data['applied_date'].isoformat()
        
        response = supabase_client.table('applications').insert(data).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating application: {str(e)}")
```

#### **Read Operations**
```python
# Get all applications
response = supabase_client.table('applications').select('*').execute()

# Get specific application
response = supabase_client.table('applications').select('*').eq('application_id', uuid).execute()

# Get user applications
response = supabase_client.table('applications').select('*').eq('user_id', user_id).execute()
```

#### **Update Operation**
```python
response = supabase_client.table('applications').update(data).eq('application_id', uuid).execute()
```

#### **Delete Operations**
```python
# Delete specific application
response = supabase_client.table('applications').delete().eq('application_id', uuid).execute()

# Bulk delete user applications
response = supabase_client.table('applications').delete().eq('user_id', user_id).execute()
```

## 🔐 Security Features

### **Authentication Flow**
1. Client includes `Authorization: Bearer <api_key>` header
2. `verify_api_key` dependency extracts and validates the token
3. Valid requests proceed to endpoint logic
4. Invalid requests return 401 Unauthorized

### **Error Handling**
- **401 Unauthorized**: Missing or invalid API key
- **404 Not Found**: Resource doesn't exist
- **500 Internal Server Error**: Server configuration or database issues

### **Input Validation**
- **Pydantic Models**: Automatic request validation
- **Type Checking**: Ensures data integrity
- **Optional Fields**: Flexible input handling
- **Date Serialization**: Proper ISO format handling

## ⚙️ Configuration

### **Environment Variables**
```env
# Database Configuration
PROJECT_URL=your_supabase_project_url
ANON_KEY=your_supabase_anon_key

# Security
API_KEY=your_secure_api_key

# Server Configuration
HOST=0.0.0.0
PORT=8000
FRONTEND_URL=http://localhost:8501
```

### **Development Setup**
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install fastapi uvicorn supabase python-dotenv

# Run development server
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## 🧪 Testing Endpoints

### **Using curl**
```bash
# Health check
curl http://localhost:8000/health

# Get applications (requires auth)
curl -H "Authorization: Bearer your_api_key" \
     http://localhost:8000/application/user/user_id

# Create application
curl -X POST \
     -H "Authorization: Bearer your_api_key" \
     -H "Content-Type: application/json" \
     -d '{"user_id":"user123","company_name":"TechCorp","job_title":"Developer"}' \
     http://localhost:8000/application/
```

### **Using Python requests**
```python
import requests

headers = {
    'Authorization': 'Bearer your_api_key',
    'Content-Type': 'application/json'
}

# Get applications
response = requests.get(
    'http://localhost:8000/application/user/user_id',
    headers=headers
)

# Create application
data = {
    'user_id': 'user123',
    'company_name': 'TechCorp',
    'job_title': 'Developer',
    'status': 'applied'
}

response = requests.post(
    'http://localhost:8000/application/',
    json=data,
    headers=headers
)
```

## 🚀 Production Deployment

### **Production Configuration**
- Use environment variables for all configuration
- Set up proper logging
- Configure HTTPS
- Use a production WSGI server (Gunicorn, uWSGI)
- Set up monitoring and health checks

### **Deployment Example (Docker)**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔧 Performance Considerations

### **Database Optimization**
- Use connection pooling for high-traffic scenarios
- Implement caching for frequently accessed data
- Add database indexes for common queries
- Consider pagination for large result sets

### **API Optimization**
- Use async/await for I/O operations
- Implement request rate limiting
- Add response compression
- Use background tasks for heavy operations

### **Monitoring**
- Add structured logging
- Implement health check endpoints
- Monitor response times and error rates
- Set up alerts for system issues

---

**This backend implementation demonstrates professional API development practices suitable for production environments.**
