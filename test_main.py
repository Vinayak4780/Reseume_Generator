from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI(title="AI Resume Builder", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>AI Resume Builder - Test</title>
        </head>
        <body>
            <h1>AI Resume Builder is Working!</h1>
            <p>Basic FastAPI server is running successfully.</p>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "AI Resume Builder API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
