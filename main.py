from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os
from pathlib import Path
from typing import Optional, List
import json
import asyncio
from dotenv import load_dotenv

from services.resume_generator import ResumeGenerator
from services.pdf_generator import PDFGenerator
from services.database_service import DatabaseService
from models.resume_models import ResumeRequest, ResumeResponse
from models.database_models import UserModel, ResumeModel

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Resume Builder", description="Professional Resume Builder using LangChain and Groq API")

# Setup static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize services
resume_generator = ResumeGenerator()
pdf_generator = PDFGenerator()
db_service = DatabaseService()

@app.on_event("startup")
async def startup_event():
    await db_service.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await db_service.disconnect()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main page with resume builder form"""
    return templates.TemplateResponse("index.html", {"request": request})

from models.resume_models import ExperienceLevel  # Add this import

@app.post("/generate-resume")
async def generate_resume(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    experience_level: str = Form(...),
    target_role: str = Form(...),
    skills: str = Form(...),
    education: str = Form(...),
    projects: str = Form(...),
    additional_info: str = Form(default="")
):
    try:
        print("Received data:", name, email, phone, experience_level, target_role, skills, education, projects, additional_info)
        # Convert experience_level string to Enum
        resume_request = ResumeRequest(
            name=name,
            email=email,
            phone=phone,
            experience_level=ExperienceLevel(experience_level),  # <-- FIXED HERE
            target_role=target_role,
            skills=skills,
            education=education,
            projects=projects,
            additional_info=additional_info
        )
        
        resume_content = await resume_generator.generate_resume(resume_request)
        
        # Save resume to database
        try:
            resume_title = f"{target_role} Resume - {resume_request.name}"
            resume_id = await db_service.save_resume(
                user_email=email,
                resume_data=resume_content,
                title=resume_title
            )
            resume_content['_id'] = resume_id  # Add ID to response
        except Exception as db_error:
            print(f"Database save error: {str(db_error)}")
            # Continue without failing - resume generation worked
        
        return {"success": True, "resume": resume_content}
    except Exception as e:
        print("Error in /generate-resume:", str(e))
        raise HTTPException(status_code=500, detail=f"Error generating resume: {str(e)}")

@app.post("/download-pdf")
async def download_pdf(resume_data: dict):
    """Generate and download PDF version of the resume"""
    try:
        print("Received PDF data structure:")
        print(json.dumps(resume_data, indent=2))
        
        # Ensure proper data structure for PDF generator
        processed_data = normalize_resume_data_for_pdf(resume_data)
        
        print("Processed PDF data structure:")
        print(json.dumps(processed_data, indent=2))
        
        # Generate PDF
        pdf_path = await pdf_generator.generate_pdf(processed_data)
        
        return FileResponse(
            path=pdf_path,
            filename=f"{processed_data.get('name', 'resume').replace(' ', '_')}_resume.pdf",
            media_type="application/pdf"
        )
        
    except Exception as e:
        print(f"PDF generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

def normalize_resume_data_for_pdf(resume_data: dict) -> dict:
    """Normalize resume data structure for PDF generation"""
    normalized = resume_data.copy()
    
    # Ensure contact_info is properly structured
    if 'contact_info' not in normalized or not isinstance(normalized.get('contact_info'), dict):
        normalized['contact_info'] = {
            'email': resume_data.get('email', ''),
            'phone': resume_data.get('phone', '')
        }
    
    # Ensure skills is a list
    if 'skills' in normalized:
        if isinstance(normalized['skills'], str):
            # Split string into list
            skills_list = [skill.strip() for skill in normalized['skills'].split(',')]
            normalized['skills'] = [skill for skill in skills_list if skill]
        elif not isinstance(normalized['skills'], list):
            normalized['skills'] = [str(normalized['skills'])]
    
    # Ensure education is a list
    if 'education' in normalized:
        if isinstance(normalized['education'], str):
            # Convert string to basic education entry
            normalized['education'] = [{
                'degree': '',
                'institution': '',
                'year': '',
                'cgpa': '',
                'details': normalized['education']
            }]
        elif not isinstance(normalized['education'], list):
            normalized['education'] = [normalized['education']]
    
    # Ensure projects is a list
    if 'projects' in normalized:
        if isinstance(normalized['projects'], str):
            # Convert string to basic project entry
            normalized['projects'] = [{
                'title': 'Projects',
                'description': normalized['projects'],
                'technologies': '',
                'duration': ''
            }]
        elif not isinstance(normalized['projects'], list):
            normalized['projects'] = [normalized['projects']]
    
    return normalized

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Resume Builder"}

# New endpoints for user authentication and resume management

@app.post("/login")
async def login_user(email: str = Form(...), name: str = Form(...)):
    """Login or create user"""
    try:
        user = await db_service.create_or_get_user(email, name)
        return {"success": True, "user": {"email": user.email, "name": user.name}}
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.get("/user/{email}/resumes")
async def get_user_resumes(email: str):
    """Get all resumes for a user"""
    try:
        resumes = await db_service.get_user_resumes(email)
        return {"success": True, "resumes": [
            {
                "id": str(resume.id),
                "title": resume.title,
                "created_at": resume.created_at.isoformat(),
                "updated_at": resume.updated_at.isoformat()
            } for resume in resumes
        ]}
    except Exception as e:
        print(f"Get resumes error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get resumes: {str(e)}")

@app.get("/resume/{resume_id}")
async def get_resume(resume_id: str, user_email: str):
    """Get a specific resume"""
    try:
        resume = await db_service.get_resume_by_id(resume_id, user_email)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        return {"success": True, "resume": resume.resume_data}
    except Exception as e:
        print(f"Get resume error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get resume: {str(e)}")

@app.delete("/resume/{resume_id}")
async def delete_resume(resume_id: str, user_email: str):
    """Delete a resume"""
    try:
        success = await db_service.delete_resume(resume_id, user_email)
        if not success:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        return {"success": True, "message": "Resume deleted successfully"}
    except Exception as e:
        print(f"Delete resume error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete resume: {str(e)}")

@app.get("/dashboard")
async def dashboard(request: Request, email: str = None):
    """User dashboard page"""
    if not email:
        return templates.TemplateResponse("login.html", {"request": request})
    
    try:
        resumes = await db_service.get_user_resumes(email)
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "user_email": email,
            "resumes": resumes
        })
    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Failed to load dashboard"
        })

if __name__ == "__main__":
    print("\nYour app is running! Open http://127.0.0.1:8000 in your browser.\n")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
