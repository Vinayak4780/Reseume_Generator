import os
import tempfile
from typing import Dict, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime

class PDFGenerator:
    """PDF generator that matches the exact web preview styling"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles optimized for single page layout"""
        
        # Resume Name - reduced size for single page
        self.styles.add(ParagraphStyle(
            name='ResumeName',
            parent=self.styles['Normal'],
            fontSize=24,  # Reduced from 36
            fontName='Times-Bold',
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            spaceBefore=0,
            spaceAfter=6,  # Reduced spacing
            leading=28
        ))
        
        # Contact Info - compact styling
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=12,  # Reduced from 16
            fontName='Times-Roman',
            textColor=colors.HexColor('#6c757d'),
            alignment=TA_CENTER,
            spaceBefore=0,
            spaceAfter=8,  # Reduced spacing
            leading=16
        ))
        
        # Section Titles - compact for single page
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Normal'],
            fontSize=14,  # Reduced from 20
            fontName='Times-Bold',
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_LEFT,
            spaceBefore=8,  # Reduced spacing
            spaceAfter=4,   # Reduced spacing
            leading=16,
            borderWidth=1,
            borderColor=colors.HexColor('#dee2e6'),
            borderPadding=0,
            leftIndent=0,
            rightIndent=0
        ))
        
        # Summary text - compact
        self.styles.add(ParagraphStyle(
            name='SummaryText',
            parent=self.styles['Normal'],
            fontSize=11,  # Reduced from 16
            fontName='Times-Roman',
            textColor=colors.HexColor('#333333'),
            alignment=TA_JUSTIFY,
            spaceBefore=0,
            spaceAfter=8,  # Reduced spacing
            leading=15,    # Reduced line height
            leftIndent=0,
            rightIndent=0
        ))
        
        # Item titles - compact
        self.styles.add(ParagraphStyle(
            name='ItemTitle',
            parent=self.styles['Normal'],
            fontSize=12,  # Reduced from 16
            fontName='Times-Bold',
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=2,  # Reduced spacing
            leading=14,
            leftIndent=8   # Reduced indent
        ))
        
        # Item details - compact
        self.styles.add(ParagraphStyle(
            name='ItemDetails',
            parent=self.styles['Normal'],
            fontSize=10,  # Reduced from 14
            fontName='Times-Roman',
            textColor=colors.HexColor('#6c757d'),
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=2,  # Reduced spacing
            leading=12,
            leftIndent=8
        ))
        
        # Regular content - compact
        self.styles.add(ParagraphStyle(
            name='RegularText',
            parent=self.styles['Normal'],
            fontSize=10,  # Reduced from 14
            fontName='Times-Roman',
            textColor=colors.HexColor('#333333'),
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=4,  # Reduced spacing
            leading=13,    # Reduced line height
            leftIndent=8
        ))
    
    def _create_header_line(self):
        """Create the blue header line that matches web design"""
        from reportlab.platypus import Table, TableStyle
        # Create a table for the blue line
        line_data = [[''] * 10]
        line_table = Table(line_data, colWidths=[inch * 0.8] * 10)
        line_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#007bff')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#007bff')]),
            ('GRID', (0, 0), (-1, -1), 2, colors.HexColor('#007bff')),
        ]))
        return line_table
    
    def _create_section_header(self, title: str):
        """Create section headers that match web styling with compact spacing"""
        # Create the section title with underline
        title_para = Paragraph(title.upper(), self.styles['SectionTitle'])
        
        # Create underline using a table
        underline_data = [['']]
        underline_table = Table(underline_data, colWidths=[7*inch], rowHeights=[0.5])
        underline_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ]))
        
        return [title_para, underline_table, Spacer(1, 3)]
    
    def _truncate_text(self, text: str, max_length: int = 500) -> str:
        """Truncate text to fit single page layout"""
        if len(text) <= max_length:
            return text
        return text[:max_length].rsplit(' ', 1)[0] + "..."
    
    def _limit_list_items(self, items: List, max_items: int = 3) -> List:
        """Limit list items to fit single page"""
        return items[:max_items] if len(items) > max_items else items

    async def generate_pdf(self, resume_data: Dict) -> str:
        """Generate PDF that exactly matches the web preview styling"""      
        try:
            print(f"PDF Generator received data keys: {list(resume_data.keys())}")
            # Create temporary PDF file
            pdf_filename = f"resume_{resume_data.get('name', 'candidate').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_path = os.path.join(self.temp_dir, pdf_filename)
            
            # Create PDF document with proper margins
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=A4,
                rightMargin=60,
                leftMargin=60,
                topMargin=60,
                bottomMargin=60
            )
            
            # Build content that matches web styling exactly
            story = []
            
            # Header section (name + contact) - matches .resume-header
            self._add_header_section(story, resume_data)
            
            # Summary section - matches .resume-summary
            self._add_summary_section(story, resume_data)
            
            # Education section - matches .education-item styling
            self._add_education_section(story, resume_data)
            
            # Skills section - matches .skills-list styling  
            self._add_skills_section(story, resume_data)
            
            # Projects section - matches .project-item styling
            self._add_projects_section(story, resume_data)
            
            # Build PDF
            doc.build(story)
            
            print(f"PDF generated successfully at: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            print(f"PDF generation error details: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Error generating PDF: {str(e)}")
    
    def _add_header_section(self, story: List, resume_data: Dict):
        """Add header section that matches .resume-header styling"""
        # Name - matches .resume-name styling (2.5rem, bold, #2c3e50, center)
        name = resume_data.get('name', 'Candidate Name')
        story.append(Paragraph(name, self.styles['ResumeName']))
        
        # Contact information - matches .resume-contact styling
        contact_info = resume_data.get('contact_info', {})
        if isinstance(contact_info, dict):
            email = contact_info.get('email', '')
            phone = contact_info.get('phone', '')
        else:
            email = resume_data.get('email', '')
            phone = resume_data.get('phone', '')
        
        if email or phone:
            contact_parts = [part for part in [email, phone] if part]
            contact_text = " | ".join(contact_parts)
            story.append(Paragraph(contact_text, self.styles['ContactInfo']))
        
        # Add blue header line that matches CSS border-bottom: 2px solid #007bff
        story.append(self._create_header_line())
        story.append(Spacer(1, 10))  # Reduced from 20
    
    def _add_summary_section(self, story: List, resume_data: Dict):
        """Add summary section that matches .resume-summary styling"""
        summary = resume_data.get('summary', '')
        if summary and summary.strip():
            # Section header
            story.extend(self._create_section_header("Professional Summary"))
            
            # Truncate summary to fit single page
            truncated_summary = self._truncate_text(summary, 400)
            
            # Summary content - matches justified text with line-height 1.7
            story.append(Paragraph(truncated_summary, self.styles['SummaryText']))
            story.append(Spacer(1, 8))  # Reduced from 20
    
    def _add_education_section(self, story: List, resume_data: Dict):
        """Add education section that matches .education-item styling"""
        education_list = resume_data.get('education', [])
        if education_list:
            # Section header
            story.extend(self._create_section_header("Education"))
            
            # Limit education items to fit single page
            limited_education = self._limit_list_items(education_list, 3)
            
            for edu in limited_education:
                if isinstance(edu, dict):
                    degree = edu.get('degree', '')
                    institution = edu.get('institution', '')
                    year = edu.get('year', '')
                    
                    # Create bordered item that matches CSS border-left: 3px solid #007bff
                    if degree:
                        # Title
                        story.append(Paragraph(degree, self.styles['ItemTitle']))
                    
                    if institution or year:
                        details_parts = [part for part in [institution, year] if part]
                        details_text = " | ".join(details_parts)
                        story.append(Paragraph(details_text, self.styles['ItemDetails']))
                    
                    story.append(Spacer(1, 8))  # Reduced spacing
                
                elif isinstance(edu, str) and edu.strip():
                    story.append(Paragraph(edu, self.styles['ItemTitle']))
                    story.append(Spacer(1, 8))  # Reduced spacing
    
    def _add_skills_section(self, story: List, resume_data: Dict):
        """Add skills section that matches .skills-list styling"""
        skills_data = resume_data.get('skills', {})
        if skills_data:
            # Section header
            story.extend(self._create_section_header("Skills"))
            
            if isinstance(skills_data, dict):
                for category, skills in skills_data.items():
                    if skills:
                        # Category name
                        story.append(Paragraph(f"<b>{category}:</b>", self.styles['ItemTitle']))
                        
                        # Skills list - matches tag-like display
                        if isinstance(skills, list):
                            skills_text = " • ".join(skills)
                        else:
                            skills_text = str(skills)
                        
                        story.append(Paragraph(skills_text, self.styles['RegularText']))
                        story.append(Spacer(1, 6))  # Reduced spacing
            
            elif isinstance(skills_data, list):
                skills_text = " • ".join(skills_data)
                story.append(Paragraph(skills_text, self.styles['RegularText']))
                story.append(Spacer(1, 6))  # Reduced spacing
            
            story.append(Spacer(1, 6))  # Reduced spacing
    
    def _add_projects_section(self, story: List, resume_data: Dict):
        """Add projects section that matches .project-item styling"""
        projects_list = resume_data.get('projects', [])
        if projects_list:
            # Section header
            story.extend(self._create_section_header("Projects"))
            
            # Limit projects to fit single page
            limited_projects = self._limit_list_items(projects_list, 3)
            
            for project in limited_projects:
                if isinstance(project, dict):
                    title = project.get('title', '')
                    description = project.get('description', '')
                    
                    # Project title - matches .project-title styling
                    if title:
                        story.append(Paragraph(title, self.styles['ItemTitle']))
                    
                    # Project description - matches regular content styling
                    if description:
                        story.append(Paragraph(description, self.styles['RegularText']))
                    
                    story.append(Spacer(1, 8))  # Reduced spacing
                
                elif isinstance(project, str) and project.strip():
                    story.append(Paragraph(project, self.styles['ItemTitle']))
                    story.append(Spacer(1, 8))  # Reduced spacing

    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass  # Ignore cleanup errors
