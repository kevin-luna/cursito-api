#!/usr/bin/env python3
"""
Main entry point for the Cursito API application.
Run this file to start the FastAPI server.
"""

import uvicorn
from src.api import app
from src.database import engine, Base

# Create database tables when starting the application
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
except Exception as e:
    print(f"⚠️  Warning: Could not create database tables: {e}")
    print("Make sure your database is running and DATABASE_URL is configured correctly.")

if __name__ == "__main__":
    uvicorn.run(
        "src.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
