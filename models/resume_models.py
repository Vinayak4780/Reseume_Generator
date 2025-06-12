
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from enum import Enum

class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    EXECUTIVE = "executive"

class ResumeRequest(BaseModel):
    """Input model for resume generation request"""
    name: str = Field(..., description="Full name of the candidate")
    email: str = Field(..., description="Email address")
    phone: str = Field(..., description="Phone number")
    experience_level: ExperienceLevel = Field(..., description="Experience level")
    target_role: str = Field(..., description="Target job role/position")
    skills: str = Field(..., description="Skills and technologies (comma-separated or detailed)")
    education: str = Field(..., description="Educational background details")
    projects: str = Field(..., description="Project details and descriptions")
    additional_info: Optional[str] = Field(default="", description="Additional information, certifications, etc.")

class ResumeSection(BaseModel):
    """Individual resume section"""
    title: str
    content: str
    order: int

class ResumeResponse(BaseModel):
    """Generated resume response"""
    name: str
    contact_info: Dict[str, str]
    summary: str
    education: List[Dict[str, str]]
    skills: List[str]
    projects: List[Dict[str, str]]
    additional_sections: Optional[List[ResumeSection]] = []

class PDFRequest(BaseModel):
    """Request model for PDF generation"""
    resume_data: ResumeResponse
    template: Optional[str] = "modern"
