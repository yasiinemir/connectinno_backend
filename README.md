Note-Taking App Backend API
This is the backend service for the Note-Taking Application, developed as part of the Connectinno Flutter Developer Case Study. The service provides a RESTful API to manage notes, integrated with Firebase/Supabase for persistent storage and authentication.

# 🚀 Features

CRUD Operations: Complete endpoints for creating, reading, updating, and deleting notes.


AI-Powered Mood Matcher (Bonus): A specialized endpoint that uses Google Gemini AI to analyze note sentiment and find matching music via yt-dlp.


Secure Access: Protected endpoints ensuring users can only access their own notes.


Robust Validation: Meaningful error handling and request validation.

# 🛠️ Tech Stack

Framework: FastAPI (Python 3.9+) 

AI Integration: Google Generative AI (Gemini 1.5 Flash)

Data Discovery: yt-dlp (Automated YouTube content search)


Environment Management: python-dotenv

# 📦 Installation & Setup

# 1.Clone the repository:

git clone <https://github.com/yasiinemir/connectinno_backend.git>
cd backend

# 2.Create a virtual environment:

python -m venv venv
source venv/bin/activate

# 3.Install dependencies:

pip install -r requirements.txt

# 4.Environment Variables: 

Copy .env.example to a new file named .env.

Add your Google Gemini API Key and Firebase/Supabase configuration.

# ▶️ Running the Server
Start the development server with:
uvicorn main:app --reload

# 🔌 API Endpoints

# GET	/notes	
List all notes for the authenticated user.

# POST	/notes	
Create a new note.

# PUT	/notes/{id}	
Update an existing note.

# DELETE	/notes/{id}	
Delete a note with the specified ID.

# POST	/recommend-music	(AI Bonus) Analyzes note text and returns a YouTube song ID.

Developed by Yasin Eren Emir - Connectinno Flutter Developer Case Study Submission
