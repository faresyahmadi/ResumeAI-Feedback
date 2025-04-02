from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
from config.config import GMAIL_CREDENTIALS, GMAIL_SENDER
import pickle
import os
from datetime import datetime

class EmailService:
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API"""
        if os.path.exists('gmail_token.pickle'):
            with open('gmail_token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    GMAIL_CREDENTIALS, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open('gmail_token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('gmail', 'v1', credentials=self.creds)
    
    def send_feedback_email(self, to_email: str, analysis: dict, comparison: dict):
        """Send resume feedback email using Gmail API"""
        # Extract name from email (everything before @)
        user_name = to_email.split('@')[0].replace('.', ' ').title()
        
        # Add name to analysis dictionary
        analysis['name'] = user_name
        
        message = self._create_message(to_email, analysis, comparison)
        
        try:
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            print(f'Message Id: {sent_message["id"]}')
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def _create_message(self, to_email: str, analysis: dict, comparison: dict):
        """Create email message for Gmail API"""
        message = MIMEText(self._create_email_content(analysis, comparison), 'html')
        message['to'] = to_email
        message['from'] = GMAIL_SENDER
        message['subject'] = "Your Resume Feedback"
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw}
    
    def _create_email_content(self, analysis: dict, comparison: dict) -> str:
        """Create HTML email content with the analysis results."""
        # Format skills section
        skills_html = ""
        if isinstance(analysis.get('strengths'), list):
            strengths_html = "<ul>"
            for strength in analysis['strengths']:
                strengths_html += f"""
                    <li><strong>{strength.get('point', '')}</strong>
                        <p>{strength.get('explanation', '')}</p>
                        <p><em>Examples:</em> {', '.join(strength.get('examples', []))}</p>
                        <p><em>Impact:</em> {strength.get('impact', '')}</p>
                    </li>"""
            strengths_html += "</ul>"

            weaknesses_html = "<ul>"
            for weakness in analysis['weaknesses']:
                weaknesses_html += f"""
                    <li><strong>{weakness.get('point', '')}</strong>
                        <p>{weakness.get('explanation', '')}</p>
                        <p><em>Examples:</em> {', '.join(weakness.get('examples', []))}</p>
                        <p><em>Impact:</em> {weakness.get('impact', '')}</p>
                    </li>"""
            weaknesses_html += "</ul>"

            skills_html = f"""
                <div class="section">
                    <h2 style="color: #2c3e50;">Your Key Strengths</h2>
                    {strengths_html}
                    <h2 style="color: #2c3e50;">Areas for Your Improvement</h2>
                    {weaknesses_html}
                </div>"""

        # Format formatting analysis
        formatting_html = ""
        if isinstance(analysis.get('formatting'), dict):
            formatting = analysis['formatting']
            formatting_html = f"""
                <div class="section">
                    <h2 style="color: #2c3e50;">Your Resume's Formatting Analysis</h2>
                    <div class="subsection">
                        <h3 style="color: #34495e;">Layout & Structure</h3>
                        <p>{formatting.get('layout', '')}</p>
                        
                        <h3 style="color: #34495e;">Visual Hierarchy</h3>
                        <p>{formatting.get('visual_hierarchy', '')}</p>
                        
                        <h3 style="color: #34495e;">Readability</h3>
                        <p>{formatting.get('readability', '')}</p>
                        
                        <h3 style="color: #34495e;">Information Organization</h3>
                        <p>{formatting.get('organization', '')}</p>
                        
                        <h3 style="color: #34495e;">Formatting Examples</h3>
                        <div class="examples">
                            <h4 style="color: #27ae60;">What You're Doing Well</h4>
                            <ul>{''.join(f'<li>{ex}</li>' for ex in formatting.get('examples', {}).get('good', []))}</ul>
                            
                            <h4 style="color: #e74c3c;">Areas You Can Improve</h4>
                            <ul>{''.join(f'<li>{ex}</li>' for ex in formatting.get('examples', {}).get('bad', []))}</ul>
                        </div>
                    </div>
                </div>"""

        # Format recommendations
        recommendations_html = ""
        if isinstance(analysis.get('recommendations'), list):
            recommendations_html = "<ul>"
            for rec in analysis['recommendations']:
                recommendations_html += f"""
                    <li>
                        <strong>{rec.get('point', '')}</strong>
                        <p><em>Why This Matters for You:</em> {rec.get('importance', '')}</p>
                        <p><em>How You Can Implement This:</em> {rec.get('implementation', '')}</p>
                        <p><em>Expected Impact on Your Resume:</em> {rec.get('impact', '')}</p>
                        <p><em>Industry Best Practices:</em> {rec.get('best_practices', '')}</p>
                    </li>"""
            recommendations_html += "</ul>"

        # Format market fit analysis
        market_fit_html = ""
        if isinstance(analysis.get('market_fit'), dict):
            market_fit = analysis['market_fit']
            market_fit_html = f"""
                <div class="section">
                    <h2 style="color: #2c3e50;">Your Market Fit Analysis</h2>
                    <div class="score-container">
                        <h3 style="color: #34495e;">Your Overall Score: {market_fit.get('score', 'N/A')}</h3>
                        <p><em>Score Justification:</em> {market_fit.get('justification', '')}</p>
                    </div>
                    
                    <div class="subsection">
                        <h3 style="color: #34495e;">Your Market Alignment</h3>
                        <p>{market_fit.get('market_alignment', '')}</p>
                        
                        <h3 style="color: #34495e;">Your Career Trajectory</h3>
                        <p>{market_fit.get('career_trajectory', '')}</p>
                        
                        <h3 style="color: #34495e;">Your Profile's Competitiveness</h3>
                        <p>{market_fit.get('competitiveness', '')}</p>
                        
                        <h3 style="color: #34495e;">Relevant Market Trends for You</h3>
                        <p>{market_fit.get('market_trends', '')}</p>
                    </div>
                </div>"""

        # Combine all sections
        content = f"""
        <div class="container">
            <div class="header">
                <p style="font-size: 16px; margin-bottom: 20px;">Dear {analysis.get('name', 'Valued User')},</p>
                <p style="font-size: 16px; margin-bottom: 20px;">Thank you for using our Resume Analysis Tool. Here's your detailed feedback.</p>
                <h1 style="color: #2c3e50;">Your Resume Analysis Report</h1>
                <p style="color: #7f8c8d;">Generated on {datetime.now().strftime('%B %d, %Y %I:%M %p')}</p>
            </div>

            {skills_html}
            {formatting_html}
            {market_fit_html}

            <div class="section">
                <h2 style="color: #2c3e50;">Your Personalized Recommendations</h2>
                {recommendations_html}
            </div>

            <div class="signature">
                <p>We hope this feedback helps you create an even stronger resume!</p>
                <p>Best regards,<br>Resume Analysis Team</p>
            </div>
        </div>"""

        return content 