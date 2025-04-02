# Resume Feedback System

This system automatically analyzes resumes uploaded to a Google Drive folder and provides detailed feedback via email. The system uses AI to analyze content and formatting, compares against best practices, and generates comprehensive feedback.

## Project Structure

```
resume_feedback/
├── config/
│   └── config.py         # Configuration settings
├── services/
│   ├── drive_service.py  # Google Drive integration
│   ├── email_service.py  # Email handling
│   ├── parser_service.py # Resume parsing
│   ├── ai_service.py     # GPT integration
│   └── supabase_service.py # Database operations
├── utils/
│   └── helpers.py        # Helper functions
├── main.py              # Main application entry point
└── requirements.txt     # Project dependencies
```

## Setup Instructions

1. Create a `.env` file with the following variables:
```
GOOGLE_DRIVE_CREDENTIALS=path_to_credentials.json
OPENAI_API_KEY=your_openai_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SMTP_SERVER=your_smtp_server
SMTP_PORT=your_smtp_port
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google Drive API:
   - Create a project in Google Cloud Console
   - Enable Google Drive API
   - Create credentials and download the JSON file
   - Place the credentials file in the config directory

4. Run the application:
```bash
python main.py
```

## Features

- Automatic resume detection from Google Drive folder
- Email extraction from resume content
- AI-powered resume analysis using GPT
- Comparison with best practices database
- Automated email feedback delivery 