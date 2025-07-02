"""
Main FastAPI application for Smart CRM SaaS.
This module initializes the FastAPI application, configures middleware,
and sets up all routes and database connections.
"""

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
from app.core.config import settings
from app.core.database import create_database_tables
from app.api import api_router

from app.core.logging_config import setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup
    logger.info("Starting Smart CRM SaaS application...")
    
    # Create database tables
    try:
        create_database_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    
    logger.info("Application startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Smart CRM SaaS application...")

from app.core.limiter import limiter

# Create FastAPI application instance
tags_metadata = [
    {
        "name": "auth",
        "description": "User authentication and authorization.",
    },
    {
        "name": "users",
        "description": "Operations with users.",
    },
    {
        "name": "clients",
        "description": "Manage clients.",
    },
    {
        "name": "projects",
        "description": "Manage projects.",
    },
    {
        "name": "financials",
        "description": "Manage financials.",
    },
    {
        "name": "ai",
        "description": "AI-powered features.",
    },
    {
        "name": "reports",
        "description": "Generate and manage reports.",
    },
    {
        "name": "notifications",
        "description": "Manage notifications.",
    },
    {
        "name": "backup",
        "description": "Backup and restore data.",
    },
    {
        "name": "api-keys",
        "description": "Manage API keys.",
    },
    {
        "name": "automated-tasks",
        "description": "Manage automated tasks.",
    },
    {
        "name": "dashboard",
        "description": "Dashboard and analytics.",
    },
    {
        "name": "root",
        "description": "Root-level endpoints.",
    },
    {
        "name": "health",
        "description": "Health check endpoints.",
    },
    {
        "name": "status",
        "description": "API status endpoints.",
    },
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A comprehensive Customer Relationship Management system for managing clients, projects, payments, and expenses.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all HTTP requests.
    
    Args:
        request (Request): The incoming HTTP request
        call_next: The next middleware or route handler
        
    Returns:
        Response: The HTTP response
    """
    start_time = time.time()
    
    # Log request details
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response details
    logger.info(
        f"Response: {response.status_code} "
        f"processed in {process_time:.4f}s"
    )
    
    # Add processing time to response headers
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions.
    
    Args:
        request (Request): The HTTP request that caused the exception
        exc (Exception): The unhandled exception
        
    Returns:
        JSONResponse: Error response with details
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": id(request)
        }
    )

# HTTP exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handler for HTTP exceptions.
    
    Args:
        request (Request): The HTTP request that caused the exception
        exc (HTTPException): The HTTP exception
        
    Returns:
        JSONResponse: Error response with details
    """
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint providing basic API information.
    
    Returns:
        dict: Basic API information and status
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "status": "running",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

from app.core.database import create_database_tables, check_database_connection

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        dict: Application health status
    """
    db_status = "connected" if check_database_connection() else "disconnected"
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.VERSION,
        "database_status": db_status
    }

# API status endpoint
@app.get("/api/status", tags=["status"])
async def api_status():
    """
    API status endpoint providing detailed system information.
    
    Returns:
        dict: Detailed API status and system information
    """
    return {
        "api_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "database": "connected",
        "endpoints": {
            "users": "/api/v1/users",
            "clients": "/api/v1/clients", 
            "projects": "/api/v1/projects",
            "payments": "/api/v1/payments",
            "expenses": "/api/v1/expenses",
            "invoices": "/api/v1/invoices",
            "financial": "/api/v1/financial"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }

# Include API routes
app.include_router(api_router)

# Development server configuration
if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting development server...")
    uvicorn.run(
        "backend_restructured.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
