import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Drive Configuration
GOOGLE_DRIVE_CREDENTIALS = os.getenv('GOOGLE_DRIVE_CREDENTIALS')
DRIVE_FOLDER_ID = os.getenv('DRIVE_FOLDER_ID')

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Gmail API Configuration
GMAIL_CREDENTIALS = os.getenv('GMAIL_CREDENTIALS')
GMAIL_SENDER = os.getenv('GMAIL_SENDER')

# File Types
ALLOWED_FILE_TYPES = ['.pdf', '.doc', '.docx']

# AI Analysis Settings
GPT_MODEL = "gpt-4"
MAX_TOKENS = 2000

# Resume Analysis Categories
ANALYSIS_CATEGORIES = [
    "content",
    "formatting",
    "keywords",
    "experience",
    "education",
    "skills"
] 