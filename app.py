from flask import Flask, render_template, request, jsonify
import os
import logging
from logging.handlers import RotatingFileHandler
from werkzeug.utils import secure_filename
from services.drive_service import DriveService
from services.ai_service import AIService
from services.email_service import EmailService
from services.supabase_service import SupabaseService
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')

file_handler = RotatingFileHandler('logs/resumeai.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)

app = Flask(__name__)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('ResumeAI startup')

# Production configurations
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize services
try:
    drive_service = DriveService()
    ai_service = AIService()
    email_service = EmailService()
    supabase_service = SupabaseService()
    app.logger.info('All services initialized successfully')
except Exception as e:
    app.logger.error(f'Failed to initialize services: {str(e)}')
    raise

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    try:
        if 'file' not in request.files:
            app.logger.warning('No file provided in request')
            return jsonify({'status': 'error', 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            app.logger.warning('Empty filename in request')
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            app.logger.warning(f'Invalid file type: {file.filename}')
            return jsonify({'status': 'error', 'message': 'Invalid file type. Please upload PDF or Word document.'}), 400
        
        if file:
            app.logger.info(f'Processing file: {file.filename}')
            
            # Save file temporarily
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # Upload to Google Drive
                app.logger.info('Uploading to Google Drive')
                drive_file = drive_service.upload_file(filepath)
                
                app.logger.info('File uploaded successfully to Google Drive')
                return jsonify({
                    'status': 'success',
                    'message': 'Resume uploaded successfully to Google Drive'
                })
                
            except Exception as e:
                app.logger.error(f'Error uploading to Google Drive: {str(e)}')
                return jsonify({
                    'status': 'error',
                    'message': 'Error uploading resume. Please try again later.'
                }), 500
                
            finally:
                # Clean up
                if os.path.exists(filepath):
                    os.remove(filepath)
                    app.logger.info('Temporary file removed')
            
    except Exception as e:
        app.logger.error(f'Unexpected error: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred. Please try again later.'
        }), 500

@app.errorhandler(413)
def too_large(e):
    app.logger.warning('File too large uploaded')
    return jsonify({
        'status': 'error',
        'message': 'File is too large. Maximum size is 100MB.'
    }), 413

@app.errorhandler(404)
def not_found(e):
    app.logger.warning(f'404 error: {request.url}')
    return jsonify({
        'status': 'error',
        'message': 'Resource not found'
    }), 404

if __name__ == '__main__':
    # Use environment variables for production settings
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host=host, port=port, debug=debug) 