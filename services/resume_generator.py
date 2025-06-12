import os
import json
from typing import Dict, List
import re

import groq
from models.resume_models import ResumeRequest, ResumeResponse

class ResumeGenerator:
    """Resume generator using Groq API directly"""
    
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.model_name = os.getenv("MODEL_NAME", "llama3-70b-8192")
        
        print("Using model:", self.model_name)  # Debug print to verify model name
        
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        # Initialize Groq client
        self.client = groq.Client(api_key=self.groq_api_key)
        
        # Resume generation prompt template
        self.resume_prompt_template = """
You are a professional resume writer with expertise in creating ATS-friendly resumes. 
Create a comprehensive, professional resume based on the following information:

CANDIDATE INFORMATION:
- Name: {name}
- Email: {email}
- Phone: {phone}
- Experience Level: {experience_level}
- Target Role: {target_role}

SKILLS:
{skills}

EDUCATION:
{education}

PROJECTS:
{projects}

ADDITIONAL INFORMATION:
{additional_info}

INSTRUCTIONS:
1. Create a professional summary (3-4 lines) that highlights the candidate's strengths and aligns with the target role
2. Format education information properly with degree, institution, year, and CGPA/GPA if provided
3. Organize skills into relevant categories (Technical Skills, Soft Skills, etc.)
4. Write detailed project descriptions with impact and technologies used
5. Use action verbs and quantify achievements where possible
6. Ensure the resume is ATS-friendly and professional
7. Follow this exact structure order: Summary, Education, Skills, Projects

Return the response in the following JSON format:
{{
    "name": "{name}",
    "contact_info": {{
        "email": "{email}",
        "phone": "{phone}"
    }},
    "summary": "Professional summary here (3-4 lines)",
    "education": [
        {{
            "degree": "Degree name",
            "institution": "Institution name",
            "year": "Year or duration",
            "cgpa": "CGPA/GPA if available",
            "details": "Additional details if any"
        }}
    ],    "skills": [
        "List of organized skills as individual strings"
    ],
    "projects": [
        {{
            "title": "Project title",
            "description": "Detailed project description with technologies and impact",
            "technologies": "Technologies used",
            "duration": "Project duration if available"
        }}
    ]
}}

Make sure the JSON is valid and properly formatted.
"""
    
    def preprocess_user_input(self, resume_request: ResumeRequest) -> Dict[str, str]:
        """Preprocess user input for better LLM understanding"""
        
        def clean_text(text: str) -> str:
            """Clean and format text input"""
            if not text:
                return ""
            # Remove extra whitespaces and normalize
            text = re.sub(r'\s+', ' ', text.strip())
            return text
        
        def process_skills(skills_text: str) -> str:
            """Process skills input to be more structured"""
            skills = clean_text(skills_text)
            if ',' in skills:
                # If comma-separated, format nicely
                skill_list = [skill.strip() for skill in skills.split(',')]
                return ', '.join(skill_list)
            return skills
        
        def process_education(education_text: str) -> str:
            """Process education input to extract key information"""
            education = clean_text(education_text)
            # Add guidance for common formats
            if education and not any(word in education.lower() for word in ['degree', 'university', 'college', 'cgpa', 'gpa']):
                education = f"Education details: {education}"
            return education
        
        def process_projects(projects_text: str) -> str:
            """Process projects input to be more structured"""
            projects = clean_text(projects_text)
            # If multiple projects, try to separate them
            if projects and len(projects.split('.')) > 2:
                # Likely multiple projects
                return projects
            return projects
        
        return {
            "name": clean_text(resume_request.name),
            "email": resume_request.email,
            "phone": clean_text(resume_request.phone),
            "experience_level": resume_request.experience_level.value,
            "target_role": clean_text(resume_request.target_role),
            "skills": process_skills(resume_request.skills),
            "education": process_education(resume_request.education),            "projects": process_projects(resume_request.projects),
            "additional_info": clean_text(resume_request.additional_info)
        }
    async def generate_resume(self, resume_request: ResumeRequest) -> Dict:
        """Generate resume content using Groq API directly"""
        try:
            # Preprocess input
            processed_input = self.preprocess_user_input(resume_request)
            
            # Generate prompt
            formatted_prompt = self.resume_prompt_template.format(**processed_input)
            
            # Ensure we're using the correct model
            current_model = os.getenv("MODEL_NAME", "llama3-70b-8192")
            print(f"API call using model: {current_model}")
            
            # Get response from Groq
            completion = self.client.chat.completions.create(
                model=current_model,  # Use current model from environment
                messages=[
                    {
                        "role": "user",
                        "content": formatted_prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            response_content = completion.choices[0].message.content
            
            # Parse JSON response
            resume_content = self._parse_resume_response(response_content)
            
            return resume_content
            
        except Exception as e:
            raise Exception(f"Error generating resume: {str(e)}")
    def _parse_resume_response(self, response_text: str) -> Dict:
        """Parse and validate the resume response"""
        try:
            # Extract JSON from response if it contains other text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No valid JSON found in response")
            
            json_text = response_text[json_start:json_end]
            resume_data = json.loads(json_text)
            
            # Validate required fields
            required_fields = ['name', 'contact_info', 'summary', 'education', 'skills', 'projects']
            for field in required_fields:
                if field not in resume_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Ensure skills is an array of strings
            skills = resume_data.get('skills', [])
            if isinstance(skills, str):
                # Convert string to array
                skills_array = [skill.strip() for skill in skills.split(',') if skill.strip()]
                resume_data['skills'] = skills_array
            elif not isinstance(skills, list):
                # Convert other types to string then to array
                skills_str = str(skills) if skills else ""
                skills_array = [skill.strip() for skill in skills_str.split(',') if skill.strip()]
                resume_data['skills'] = skills_array
            
            return resume_data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in response: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing resume response: {str(e)}")
    
    def enhance_resume_content(self, resume_data: Dict, target_role: str) -> Dict:
        """Enhance resume content for specific role targeting"""
        # This method can be extended to add role-specific enhancements
        return resume_data
