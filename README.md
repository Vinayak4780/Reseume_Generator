# AI Resume Builder 🚀

An intelligent resume builder that leverages AI to generate professional, ATS-friendly resumes. Built with FastAPI, Python, and modern web technologies.

## ✨ Features

- 🤖 **AI-Powered Resume Generation** - Uses Groq's LLaMA 3 70B model for intelligent content creation
- 📝 **Smart Form Validation** - Real-time validation with user-friendly feedback
- 📄 **PDF Export** - Generate professional PDF resumes instantly
- 💾 **Database Integration** - Save and manage multiple resumes with MongoDB
- 👤 **User Management** - Login system with personal dashboard
- 📱 **Responsive Design** - Works seamlessly on desktop and mobile devices
- ⚡ **Real-time Preview** - See your resume as you build it
- 🎨 **Professional Templates** - Clean, modern resume layouts

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Python 3.11+** - Core programming language
- **MongoDB** - NoSQL database for data storage
- **Groq API** - AI model integration (LLaMA 3 70B)
- **ReportLab** - PDF generation library
- **Motor** - Async MongoDB driver

### Frontend
- **HTML5/CSS3** - Modern web standards
- **JavaScript (ES6+)** - Interactive functionality
- **Bootstrap 5** - Responsive UI framework
- **Font Awesome** - Icon library

### Development
- **Uvicorn** - ASGI server
- **Jinja2** - Template engine
- **python-dotenv** - Environment variable management

## 📁 Project Structure

```
AI Resume Builder/
│
├── main.py                     # FastAPI application entry point
├── requirements.txt           # Python dependencies
├── test_main.py              # Test configurations
├── README.md                 # Project documentation
├── .gitignore               # Git ignore rules
├── .env                     # Environment variables (not in repo)
│
├── models/                  # Data models
│   ├── __init__.py
│   ├── database_models.py   # MongoDB document models
│   └── resume_models.py     # Resume data structures
│
├── services/                # Business logic
│   ├── __init__.py
│   ├── resume_generator.py  # AI resume generation service
│   ├── pdf_generator.py     # PDF creation service
│   ├── pdf_generator_fixed.py # Enhanced PDF service
│   └── database_service.py  # MongoDB operations
│
├── static/                  # Static assets
│   ├── script.js           # Frontend JavaScript
│   └── style.css           # Custom styles
│
└── templates/              # HTML templates
    ├── index.html          # Main resume builder page
    ├── dashboard.html      # User dashboard
    └── login.html          # Login/signup page
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- MongoDB Atlas account (or local MongoDB)
- Groq API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Vinayak4780/Reseume_Generator.git
   cd Reseume_Generator
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   # Groq AI Configuration
   GROQ_API_KEY=your_groq_api_key_here
   MODEL_NAME=llama3-70b-8192
   
   # MongoDB Configuration
   MONGODB_CONNECTION_STRING=your_mongodb_connection_string
   DATABASE_NAME=resume_builder
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Access the application**
   
   Open your browser and navigate to: `http://127.0.0.1:8000`

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Your Groq API key for AI functionality | Yes |
| `MODEL_NAME` | AI model to use (default: llama3-70b-8192) | No |
| `MONGODB_CONNECTION_STRING` | MongoDB Atlas or local connection string | Yes |
| `DATABASE_NAME` | Database name (default: resume_builder) | No |

### Getting API Keys

1. **Groq API Key**:
   - Visit [Groq Console](https://console.groq.com/)
   - Sign up for an account
   - Navigate to API Keys section
   - Generate a new API key

2. **MongoDB Setup**:
   - Create account at [MongoDB Atlas](https://www.mongodb.com/atlas)
   - Create a new cluster
   - Get connection string from "Connect" → "Connect your application"

## 📖 Usage

### Creating a Resume

1. **Fill the Form**:
   - Enter personal information (name, email, phone)
   - Select experience level (Entry, Mid, Senior, Executive)
   - Specify target role
   - Add skills, education, and projects

2. **Generate Resume**:
   - Click "Generate Resume" button
   - AI will process your information
   - View the generated resume in real-time

3. **Download PDF**:
   - Click "Download PDF" to save your resume
   - PDF will be automatically downloaded

### Managing Resumes

1. **Login/Register**:
   - Click "Login" in the top navigation
   - Enter email and name to create account or login

2. **Dashboard**:
   - View all your saved resumes
   - Download, view, or delete existing resumes
   - Create new resumes

## 🔧 API Endpoints

### Core Endpoints

- `GET /` - Main resume builder page
- `POST /generate-resume` - Generate new resume with AI
- `POST /download-pdf` - Convert resume to PDF
- `GET /health` - Health check endpoint

### User Management

- `POST /login` - User login/registration
- `GET /dashboard` - User dashboard page
- `GET /user/{email}/resumes` - Get user's resumes

### Resume Management

- `GET /resume/{resume_id}` - Get specific resume
- `DELETE /resume/{resume_id}` - Delete resume

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🐛 Troubleshooting

### Common Issues

**MongoDB Connection Error**:
```
Failed to connect to MongoDB: SSL handshake failed
```
- Check your MongoDB connection string
- Ensure your IP is whitelisted in MongoDB Atlas
- Verify your MongoDB credentials

**Groq API Error**:
```
Error generating resume: Invalid API key
```
- Verify your GROQ_API_KEY in `.env` file
- Check if you have sufficient API credits
- Ensure the API key is active

**PDF Generation Error**:
```
Error generating PDF
```
- Check if all required resume data is present
- Ensure ReportLab dependencies are installed
- Verify file write permissions

**Port Already in Use**:
```
Address already in use
```
- Kill existing processes: `taskkill /f /im python.exe` (Windows)
- Change port in main.py: `uvicorn.run(..., port=8001)`

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Groq](https://groq.com/) - Ultra-fast AI inference
- [MongoDB](https://www.mongodb.com/) - Document database
- [Bootstrap](https://getbootstrap.com/) - CSS framework
- [ReportLab](https://www.reportlab.com/) - PDF generation

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/Vinayak4780/Reseume_Generator/issues) page
2. Create a new issue with detailed description
3. Include error messages and environment details

---

⭐ **Star this repo if you find it helpful!** ⭐