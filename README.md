AI Music Recommendation Backend
This repository contains the backend service for the Note Taking Application case study. It is a FastAPI application that processes text input to perform sentiment analysis via Google Gemini API and retrieves relevant video content using yt-dlp.

Overview
The service exposes a REST API endpoint that:

Receives a text note from the mobile client.

Analyzes the text's sentiment using an LLM (Gemini 1.5 Flash).

Searches YouTube for a matching song based on the sentiment.

Returns the video ID and metadata to the client.

Tech Stack
Language: Python 3.9+

Framework: FastAPI

Utilities: Pydantic (Validation), python-dotenv (Env management)