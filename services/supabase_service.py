from supabase import create_client
from config.config import SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY, GPT_MODEL
from openai import OpenAI
import json

class SupabaseService:
    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def get_documents(self) -> list:
        """Retrieve documents from the database"""
        response = self.supabase.table('documents').select('*').execute()
        return response.data
    
    def get_job_descriptions(self) -> list:
        """Retrieve job descriptions from the database"""
        response = self.supabase.table('documents')\
            .select('*')\
            .eq('category', 'job_description')\
            .limit(5)\
            .execute()
        print(f"Found {len(response.data)} job descriptions (limited to 5)")  # Debug log
        return response.data
    
    def compare_with_job_descriptions(self, analysis: dict) -> dict:
        """Analyze resume against general job market requirements"""
        job_descriptions = self.get_job_descriptions()
        
        if not job_descriptions:
            print("No job descriptions found in database")  # Debug log
            return {
                'market_fit': {
                    'overall_score': 0,
                    'analysis': "No job descriptions available for analysis"
                },
                'common_requirements': [],
                'recommendations': []
            }
        
        # Get the resume content from the analysis
        resume_content = analysis.get('raw_text', '')
        if not resume_content:
            print("No resume content found in analysis")  # Debug log
            return {
                'market_fit': {
                    'overall_score': 0,
                    'analysis': "No resume content available for analysis"
                },
                'common_requirements': [],
            'recommendations': []
        }
        
        print(f"Analyzing resume against {len(job_descriptions)} job descriptions")  # Debug log
        
        # Create a prompt for GPT to analyze the overall market fit
        prompt = f"""Analyze this candidate's resume against the general job market requirements based on these job descriptions.

Job Descriptions:
{chr(10).join(job.get('content', '') for job in job_descriptions)}

Resume Content:
{resume_content}

Please provide a comprehensive analysis in JSON format with the following structure:
{{
    "market_fit": {{
        "overall_score": <number between 0-100>,
        "analysis": "<detailed analysis of how well the candidate fits the general market requirements>"
    }},
    "common_requirements": [
        {{
            "requirement": "<common requirement found across jobs>",
            "candidate_fit": "<how well the candidate meets this requirement>"
        }}
    ],
    "recommendations": [
        {{
            "type": "skills" or "experience" or "general",
            "message": "<specific recommendation for improvement>"
        }}
    ]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert HR professional analyzing how well a candidate fits the general job market requirements. Provide detailed, specific analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            # Parse GPT's response
            market_analysis = response.choices[0].message.content
            print(f"GPT Market Analysis Response: {market_analysis[:100]}...")  # Debug log
            
            # Try to parse the JSON response
            try:
                market_analysis = json.loads(market_analysis)
            except json.JSONDecodeError:
                print("Error parsing JSON, using eval")  # Debug log
                market_analysis = eval(market_analysis)
            
            return market_analysis
                    
        except Exception as e:
            print(f"Error analyzing market fit: {str(e)}")  # Debug log
            return {                                                        
                'market_fit': {
                    'overall_score': 0,
                    'analysis': f"Error during analysis: {str(e)}"
                },
                'common_requirements': [],
                'recommendations': []
            }
    
    def _extract_required_skills(self, job_content: str) -> list:
        """Extract required skills from job description"""
        # Split content into lines and clean each line
        lines = [line.strip().lower() for line in job_content.split('\n') if line.strip()]
        
        # Common skill keywords and their variations
        skill_keywords = {
            'programming': ['programming', 'coding', 'development', 'developer', 'engineer'],
            'python': ['python', 'py'],
            'java': ['java', 'jdk', 'jvm'],
            'javascript': ['javascript', 'js', 'node.js', 'nodejs'],
            'sql': ['sql', 'database', 'mysql', 'postgresql', 'oracle'],
            'aws': ['aws', 'amazon web services', 'cloud'],
            'docker': ['docker', 'container', 'kubernetes', 'k8s'],
            'agile': ['agile', 'scrum', 'sprint', 'kanban'],
            'project_management': ['project management', 'pm', 'project manager'],
            'leadership': ['leadership', 'lead', 'manage', 'management'],
            'communication': ['communication', 'communicate', 'presentation'],
            'problem_solving': ['problem solving', 'analytical', 'analysis'],
            'teamwork': ['teamwork', 'collaboration', 'team player'],
            'creativity': ['creativity', 'creative', 'innovation']
        }
        
        found_skills = []
        for line in lines:
            # Check each line against skill keywords
            for skill_category, keywords in skill_keywords.items():
                if any(keyword in line for keyword in keywords):
                    found_skills.append(skill_category.replace('_', ' ').title())
                    break  # Stop checking other keywords once a match is found
        
        return list(set(found_skills))  # Remove duplicates
    
    def _extract_required_experience(self, job_content: str) -> list:
        """Extract required experience from job description"""
        # Split content into lines and clean each line
        lines = [line.strip().lower() for line in job_content.split('\n') if line.strip()]
        
        # Experience-related keywords
        experience_keywords = [
            'years of experience',
            'experience in',
            'proven track record',
            'demonstrated experience',
            'background in',
            'expertise in',
            'minimum experience',
            'required experience'
        ]
        
        found_experience = []
        for line in lines:
            # Check if line contains experience keywords
            if any(keyword in line for keyword in experience_keywords):
                # Clean up the line and add it to found experience
                experience = line.strip()
                if experience not in found_experience:
                    found_experience.append(experience)
        
        return found_experience
    
    def _calculate_match_score(self, resume_items: list, required_items: list) -> float:
        """Calculate match score between resume items and required items"""
        if not required_items:
            return 1.0  # If no requirements specified, consider it a perfect match
        
        matches = 0
        for required in required_items:
            if any(required.lower() in item.lower() for item in resume_items):
                matches += 1
        
        return matches / len(required_items)
    
    def _generate_recommendations(self, missing_skills: list, required_experience: list, resume_experience: list) -> list:
        """Generate recommendations based on gaps"""
        recommendations = []
        
        # Skill-based recommendations
        if missing_skills:
            recommendations.append({
                'type': 'skills',
                'message': f"Consider gaining experience in: {', '.join(missing_skills)}"
            })
        
        # Experience-based recommendations
        if required_experience and not resume_experience:
            recommendations.append({
                'type': 'experience',
                'message': "Consider gaining more relevant work experience in this field"
            })
        
        return recommendations 