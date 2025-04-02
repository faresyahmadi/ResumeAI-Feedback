import time
from datetime import datetime, timedelta
from services.drive_service import DriveService
from services.parser_service import ResumeParser
from services.ai_service import AIService
from services.supabase_service import SupabaseService
from services.email_service import EmailService

class ResumeFeedbackSystem:
    def __init__(self):
        self.drive_service = DriveService()
        self.parser = ResumeParser()
        self.ai_service = AIService()
        self.supabase_service = SupabaseService()
        self.email_service = EmailService()
        self.last_check_time = datetime.now() - timedelta(minutes=1)
    
    def process_new_resumes(self):
        """Main process to handle new resume uploads"""
        while True:
            try:
                # Get new files from Google Drive
                new_files = self.drive_service.get_new_files(self.last_check_time.isoformat())
                
                for file in new_files:
                    print(f"Processing file: {file['name']}")
                    
                    # Download file
                    file_content = self.drive_service.download_file(file['id'])
                    
                    # Parse resume
                    resume_info = self.parser.parse_file(file_content, file['name'])
                    
                    if not resume_info['email']:
                        print(f"No email found in resume: {file['name']}")
                        continue
                    
                    # Analyze resume with AI
                    analysis = self.ai_service.analyze_resume(resume_info['raw_text'])
                    
                    # Add raw text to analysis for comparison
                    analysis['raw_text'] = resume_info['raw_text']
                    
                    # Compare with job descriptions
                    comparison = self.supabase_service.compare_with_job_descriptions(analysis)
                    
                    # Send feedback email
                    if self.email_service.send_feedback_email(
                        resume_info['email'],
                        analysis,
                        comparison
                    ):
                        print(f"Successfully processed resume for: {resume_info['email']}")
                        # Delete the file after successful processing
                        if self.drive_service.delete_file(file['id']):
                            print(f"Successfully deleted file: {file['name']}")
                        else:
                            print(f"Failed to delete file: {file['name']}")
                
                # Update last check time
                self.last_check_time = datetime.now()
                
                # Wait before next check
                time.sleep(60)
                
            except Exception as e:
                print(f"Error in main process: {str(e)}")
                time.sleep(60)

if __name__ == "__main__":
    system = ResumeFeedbackSystem()
    system.process_new_resumes() 