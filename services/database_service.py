import os
from datetime import datetime
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from models.database_models import UserModel, ResumeModel
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        # MongoDB connection string - add this to your .env file
        self.connection_string = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017")
        self.database_name = os.getenv("DATABASE_NAME", "resume_builder")
        self.client = None
        self.db = None
        self.connected = False
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.connection_string)
            self.db = self.client[self.database_name]
            # Test the connection
            await self.client.admin.command('ping')
            self.connected = True
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.warning(f"Failed to connect to MongoDB: {e}. Running in offline mode.")
            self.connected = False
        
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self.connected = False
      # User operations
    async def create_or_get_user(self, email: str, name: str) -> UserModel:
        """Create a new user or get existing user"""
        if not self.connected:
            # Return a mock user for offline mode
            return UserModel(
                id=ObjectId(),
                email=email,
                name=name,
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow()
            )
            
        users_collection = self.db.users
        
        # Check if user exists
        existing_user = await users_collection.find_one({"email": email})
        if existing_user:
            # Update last login
            await users_collection.update_one(
                {"email": email},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            return UserModel(**existing_user)
        
        # Create new user
        user_data = {
            "email": email,
            "name": name,
            "created_at": datetime.utcnow(),
            "last_login": datetime.utcnow()
        }
        
        result = await users_collection.insert_one(user_data)
        user_data["id"] = result.inserted_id
        return UserModel(**user_data)
    
    # Resume operations
    async def save_resume(self, user_email: str, resume_data: dict, title: str, pdf_url: str = None) -> str:
        """Save a resume to the database"""
        if not self.connected:
            # Return a mock resume ID for offline mode
            logger.warning("Database not connected. Resume not saved.")
            return str(ObjectId())
            
        resumes_collection = self.db.resumes
        
        resume_doc = {
            "user_email": user_email,
            "resume_data": resume_data,
            "pdf_url": pdf_url,
            "title": title,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        
        result = await resumes_collection.insert_one(resume_doc)
        return str(result.inserted_id)
    async def get_user_resumes(self, user_email: str) -> List[ResumeModel]:
        """Get all resumes for a user"""
        if not self.connected:
            # Return empty list for offline mode
            logger.warning("Database not connected. Cannot retrieve resumes.")
            return []
            
        resumes_collection = self.db.resumes
        
        cursor = resumes_collection.find(
            {"user_email": user_email, "is_active": True}
        ).sort("updated_at", -1)
        
        resumes = []
        async for resume_doc in cursor:
            resume_doc["id"] = resume_doc["_id"]
            resumes.append(ResumeModel(**resume_doc))
        
        return resumes
    
    async def get_resume_by_id(self, resume_id: str, user_email: str) -> Optional[ResumeModel]:
        """Get a specific resume by ID"""
        if not self.connected:
            # Return None for offline mode
            logger.warning("Database not connected. Cannot retrieve resume.")
            return None
            
        resumes_collection = self.db.resumes
        
        resume_doc = await resumes_collection.find_one({
            "_id": ObjectId(resume_id),
            "user_email": user_email,
            "is_active": True
        })
        
        if resume_doc:
            resume_doc["id"] = resume_doc["_id"]
            return ResumeModel(**resume_doc)
        return None
    
    async def update_resume(self, resume_id: str, user_email: str, resume_data: dict, title: str = None) -> bool:
        """Update an existing resume"""
        if not self.connected:
            # Return False for offline mode
            logger.warning("Database not connected. Cannot update resume.")
            return False
            
        resumes_collection = self.db.resumes
        
        update_data = {
            "resume_data": resume_data,
            "updated_at": datetime.utcnow()
        }
        
        if title:
            update_data["title"] = title
        
        result = await resumes_collection.update_one(
            {"_id": ObjectId(resume_id), "user_email": user_email},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def delete_resume(self, resume_id: str, user_email: str) -> bool:
        """Soft delete a resume"""
        if not self.connected:
            # Return False for offline mode
            logger.warning("Database not connected. Cannot delete resume.")
            return False
            
        resumes_collection = self.db.resumes
        
        result = await resumes_collection.update_one(
            {"_id": ObjectId(resume_id), "user_email": user_email},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        
        return result.modified_count > 0
