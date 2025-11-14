#!/usr/bin/env python3
"""
Simple startup script for the Social Scoring System API.

Run this to start the Flask development server.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.presentation.app import create_app
    
    if __name__ == '__main__':
        # Create app with development config
        app = create_app({
            'DEBUG': True,
            'SECRET_KEY': 'dev-secret-key-change-in-production',
            'JWT_SECRET': 'jwt-secret-change-in-production'
        })
        
        print("🚀 Starting Social Scoring System API...")
        print("📚 API Documentation available at: http://localhost:5000/api/v1/info")
        print("💚 Health check available at: http://localhost:5000/health")
        print("")
        print("📋 Available Endpoints:")
        print("  • Person API: http://localhost:5000/api/v1/person/")
        print("  • Activity API: http://localhost:5000/api/v1/activity/")
        print("  • Action API: http://localhost:5000/api/v1/action/")
        print("")
        
        # Start the development server
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=True
        )
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("")
    print("📦 Please install dependencies first:")
    print("  pip install -r requirements.txt")
    print("")
    print("🏗️ Note: Some infrastructure components are not yet implemented.")
    print("   The app will need in-memory implementations to run.")
    sys.exit(1)
    
except Exception as e:
    print(f"💥 Error starting application: {e}")
    sys.exit(1)