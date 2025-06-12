// JavaScript for AI Resume Builder

class ResumeBuilder {
    constructor() {
        this.form = document.getElementById('resumeForm');
        this.generateBtn = document.getElementById('generateBtn');
        this.downloadPdfBtn = document.getElementById('downloadPdfBtn');
        this.editBtn = document.getElementById('editBtn');
        this.previewContent = document.getElementById('previewContent');
        this.previewActions = document.getElementById('previewActions');
        this.loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
        
        this.currentResumeData = null;
        this.isGenerating = false;
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        this.downloadPdfBtn.addEventListener('click', () => this.downloadPDF());
        this.editBtn.addEventListener('click', () => this.editResume());
        
        // Real-time form validation
        this.form.addEventListener('input', () => this.validateForm());
    }
    
    async handleFormSubmit(event) {
        event.preventDefault();
        
        if (!this.validateForm()) {
            this.form.classList.add('was-validated');
            this.showError('Please fill in all required fields correctly.');
            return;
        }
        
        if (this.isGenerating) {
            return;
        }
        
        this.isGenerating = true;
        this.showLoading();
        
        try {
            const formData = new FormData(this.form);
            const response = await fetch('/generate-resume', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.currentResumeData = result.resume;
                this.displayResume(result.resume);
                this.showPreviewActions();
            } else {
                this.showError('Failed to generate resume. Please try again.');
            }
        } catch (error) {
            console.error('Error generating resume:', error);
            this.showError('An error occurred while generating your resume. Please check your internet connection and try again.');
        } finally {
            this.hideLoading();
            this.isGenerating = false;
        }
    }
    
    validateForm() {
        const requiredFields = [
            'name', 'email', 'phone', 'experience_level', 
            'target_role', 'skills', 'education', 'projects'
        ];
        
        let isValid = true;
        
        requiredFields.forEach(fieldName => {
            const field = document.getElementById(fieldName);
            if (!field.value.trim()) {
                isValid = false;
            }
        });
        
        // Email validation
        const email = document.getElementById('email');
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email.value)) {
            isValid = false;
        }
        
        // Update generate button state
        this.generateBtn.disabled = !isValid || this.isGenerating;
        
        return isValid;
    }
    
    displayResume(resumeData) {
        const resumeHtml = this.generateResumeHTML(resumeData);
        this.previewContent.innerHTML = resumeHtml;
        this.previewContent.classList.add('success-animation');
        
        // Remove animation class after animation completes
        setTimeout(() => {
            this.previewContent.classList.remove('success-animation');
        }, 500);
    }
    
    generateResumeHTML(data) {
        return `
            <div class="resume-content">
                <!-- Header -->
                <div class="resume-header">
                    <h1 class="resume-name">${data.name}</h1>
                    <div class="resume-contact">
                        ${data.contact_info.email} | ${data.contact_info.phone}
                    </div>
                </div>
                
                <!-- Professional Summary -->
                <div class="resume-section">
                    <h2 class="resume-section-title">Professional Summary</h2>
                    <div class="resume-summary">${data.summary}</div>
                </div>
                
                <!-- Education -->
                <div class="resume-section">
                    <h2 class="resume-section-title">Education</h2>
                    ${this.generateEducationHTML(data.education)}
                </div>
                
                <!-- Skills -->
                <div class="resume-section">
                    <h2 class="resume-section-title">Technical Skills</h2>
                    ${this.generateSkillsHTML(data.skills)}
                </div>
                
                <!-- Projects -->
                <div class="resume-section">
                    <h2 class="resume-section-title">Projects</h2>
                    ${this.generateProjectsHTML(data.projects)}
                </div>
            </div>
        `;
    }
    
    generateEducationHTML(education) {
        if (!Array.isArray(education)) return '';
        
        return education.map(edu => `
            <div class="education-item">
                <div class="education-degree">${edu.degree || ''}</div>
                <div class="education-details">
                    ${edu.institution || ''} ${edu.year ? `(${edu.year})` : ''}
                    ${edu.cgpa ? ` | CGPA: ${edu.cgpa}` : ''}
                </div>
                ${edu.details ? `<div class="education-details">${edu.details}</div>` : ''}
            </div>
        `).join('');
    }
      generateSkillsHTML(skills) {
        if (Array.isArray(skills)) {
            return `
                <div class="skills-list">
                    ${skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                </div>
            `;
        } else if (typeof skills === 'string') {
            const skillsArray = skills.split(/[,;•]/).map(s => s.trim()).filter(s => s.length > 0);
            return `
                <div class="skills-list">
                    ${skillsArray.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                </div>
            `;
        } else if (typeof skills === 'object' && skills !== null) {
            // Handle object/dict case - extract values or convert to string
            let skillsText = '';
            if (skills.toString && skills.toString() !== '[object Object]') {
                skillsText = skills.toString();
            } else {
                // Try to extract meaningful data from object
                skillsText = Object.values(skills).join(', ');
            }
            
            if (skillsText) {
                const skillsArray = skillsText.split(/[,;•]/).map(s => s.trim()).filter(s => s.length > 0);
                return `
                    <div class="skills-list">
                        ${skillsArray.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                    </div>
                `;
            }
        }
        return '<div>No skills listed</div>';
    }
    
    generateProjectsHTML(projects) {
        if (!Array.isArray(projects)) return '';
        
        return projects.map(project => `
            <div class="project-item">
                <div class="project-title">${project.title || 'Untitled Project'}</div>
                ${project.duration ? `<div class="project-details">Duration: ${project.duration}</div>` : ''}
                <div class="project-description">${project.description || ''}</div>
                ${project.technologies ? `<div class="project-details"><strong>Technologies:</strong> ${project.technologies}</div>` : ''}
            </div>
        `).join('');
    }    async downloadPDF() {
        if (!this.currentResumeData) {
            this.showError('No resume data available for download.');
            return;
        }
        
        try {
            // Show a simple loading state on the button instead of modal
            const originalText = this.downloadPdfBtn.innerHTML;
            this.downloadPdfBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Downloading...';
            this.downloadPdfBtn.disabled = true;
            
            const response = await fetch('/download-pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.currentResumeData)
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${this.currentResumeData.name.replace(/\s+/g, '_')}_resume.pdf`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                // Reset button and show success
                this.downloadPdfBtn.innerHTML = originalText;
                this.downloadPdfBtn.disabled = false;
                
                this.showSuccess('Resume downloaded successfully!');
            } else {
                const errorText = await response.text();
                console.error('PDF generation failed:', errorText);
                
                // Reset button
                this.downloadPdfBtn.innerHTML = originalText;
                this.downloadPdfBtn.disabled = false;
                
                this.showError(`Failed to generate PDF: ${response.status}`);
            }
        } catch (error) {
            console.error('Error downloading PDF:', error);
            
            // Reset button
            const originalText = 'Download PDF';
            this.downloadPdfBtn.innerHTML = originalText;
            this.downloadPdfBtn.disabled = false;
            
            this.showError('Failed to download PDF. Please try again.');
        }
    }
    
    editResume() {
        // Scroll to top of form
        this.form.scrollIntoView({ behavior: 'smooth' });
        
        // Focus on first input
        document.getElementById('name').focus();
    }
    
    showPreviewActions() {
        this.previewActions.style.display = 'flex';
    }
    
    hidePreviewActions() {
        this.previewActions.style.display = 'none';
    }    showLoading(message = 'Generating Your Resume...') {
        try {
            // This modal should only be used for resume generation
            const modalBody = document.querySelector('#loadingModal .modal-body');
            const messageElement = modalBody.querySelector('h5');
            if (messageElement) {
                messageElement.textContent = message;
            }
            
            console.log('Showing loading modal for resume generation:', message);
            this.loadingModal.show();
        } catch (error) {
            console.error('Error showing loading modal:', error);
        }
    }hideLoading() {
        try {
            console.log('Hiding loading modal');
            
            // Hide the Bootstrap modal
            this.loadingModal.hide();
            
            // Comprehensive cleanup to ensure modal is fully hidden
            setTimeout(() => {
                const modalElement = document.getElementById('loadingModal');
                const backdrop = document.querySelector('.modal-backdrop');
                
                // Force remove modal classes and backdrop
                if (modalElement) {
                    modalElement.classList.remove('show');
                    modalElement.style.display = 'none';
                    modalElement.setAttribute('aria-hidden', 'true');
                    modalElement.removeAttribute('aria-modal');
                    modalElement.removeAttribute('role');
                }
                
                // Remove any lingering backdrop
                if (backdrop) {
                    backdrop.remove();
                }
                
                // Clean up body classes and styles
                document.body.classList.remove('modal-open');
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
                
                console.log('Loading modal cleanup completed');
            }, 50);
            
        } catch (error) {
            console.error('Error hiding loading modal:', error);
            
            // Fallback: Force hide modal manually
            const modalElement = document.getElementById('loadingModal');
            if (modalElement) {
                modalElement.style.display = 'none';
                modalElement.classList.remove('show');
                modalElement.setAttribute('aria-hidden', 'true');
                
                // Clean up backdrop
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) {
                    backdrop.remove();
                }
                
                // Clean up body classes
                document.body.classList.remove('modal-open');
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
            }
        }
    }
    
    showError(message) {
        this.showToast(message, 'danger');
    }
    
    showSuccess(message) {
        this.showToast(message, 'success');
    }
    
    showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast
        const toastId = 'toast_' + Date.now();
        const toastHTML = `
            <div class="toast align-items-center text-bg-${type} border-0" role="alert" id="${toastId}">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        
        // Show toast
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 5000
        });
        toast.show();
        
        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }
}

// Initialize the resume builder when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new ResumeBuilder();
});

// Add some helper functions for form enhancement
document.addEventListener('DOMContentLoaded', function() {
    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });
    
    // Add character count for important fields
    const importantFields = ['skills', 'education', 'projects'];
    importantFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            const counter = document.createElement('div');
            counter.className = 'form-text text-muted';
            counter.style.textAlign = 'right';
            field.parentNode.appendChild(counter);
            
            function updateCounter() {
                const count = field.value.length;
                counter.textContent = `${count} characters`;
                counter.style.color = count > 1000 ? '#dc3545' : '#6c757d';
            }
            
            field.addEventListener('input', updateCounter);
            updateCounter();
        }
    });
});
