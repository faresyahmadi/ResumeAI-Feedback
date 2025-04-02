from openai import OpenAI
from config.config import OPENAI_API_KEY, GPT_MODEL, MAX_TOKENS, ANALYSIS_CATEGORIES
import json

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def analyze_resume(self, resume_text: str) -> dict:
        """Analyze resume content using GPT"""
        prompt = self._create_analysis_prompt(resume_text)
        
        response = self.client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert resume reviewer. Analyze the resume and provide detailed feedback."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=MAX_TOKENS,
            temperature=0.7
        )
        
        return self._parse_ai_response(response.choices[0].message.content)
    
    def _create_analysis_prompt(self, resume_text: str) -> str:
        """Create a detailed prompt for resume analysis."""
        return f"""You are an expert resume reviewer with extensive experience in technical hiring. 
        First, extract the candidate's full name from the resume. Then analyze the resume and provide a detailed, comprehensive evaluation focusing on the following specific aspects:

        1. CANDIDATE NAME:
        - Extract the candidate's full name from the resume
        - If multiple names appear, use the most prominent one (usually at the top)
        - Format the name properly with correct capitalization

        2. STRENGTHS (Provide exactly 2 key strengths):
        - For each strength, provide a detailed explanation of why it's valuable
        - Include specific examples from the resume
        - Explain how these strengths benefit potential employers

        3. WEAKNESSES (Provide exactly 2 key weaknesses):
        - For each weakness, explain why it's a concern
        - Provide specific examples from the resume
        - Suggest how these weaknesses could impact career opportunities

        4. FORMATTING EVALUATION:
        - Analyze the overall layout and structure
        - Evaluate the use of white space and visual hierarchy
        - Assess the readability and professional appearance
        - Comment on the organization of information
        - Provide specific examples of good and bad formatting choices

        5. IMPROVEMENT RECOMMENDATIONS:
        - Provide 3-4 detailed, actionable recommendations
        - For each recommendation:
          * Explain why it's important
          * Provide specific examples of how to implement it
          * Describe the expected impact
          * Include industry best practices

        6. MARKET FIT ANALYSIS:
        - Provide an overall score (0-100) with detailed justification
        - Analyze how well the resume aligns with current market demands
        - Evaluate the candidate's career trajectory
        - Assess the competitiveness of their profile
        - Include specific market trends and requirements

        Resume Text:
{resume_text}

        Provide your analysis in the following JSON format:
        {{
            "candidate_name": "Full Name of the Candidate",
            "strengths": [
                {{
                    "point": "Detailed strength description",
                    "explanation": "Comprehensive explanation of why this is valuable",
                    "examples": ["Specific example 1", "Specific example 2"],
                    "impact": "How this benefits potential employers"
                }},
                {{
                    "point": "Detailed strength description",
                    "explanation": "Comprehensive explanation of why this is valuable",
                    "examples": ["Specific example 1", "Specific example 2"],
                    "impact": "How this benefits potential employers"
                }}
            ],
            "weaknesses": [
                {{
                    "point": "Detailed weakness description",
                    "explanation": "Comprehensive explanation of why this is a concern",
                    "examples": ["Specific example 1", "Specific example 2"],
                    "impact": "How this could affect career opportunities"
                }},
                {{
                    "point": "Detailed weakness description",
                    "explanation": "Comprehensive explanation of why this is a concern",
                    "examples": ["Specific example 1", "Specific example 2"],
                    "impact": "How this could affect career opportunities"
                }}
            ],
            "formatting": {{
                "layout": "Detailed analysis of layout and structure",
                "visual_hierarchy": "Detailed analysis of visual hierarchy",
                "readability": "Detailed analysis of readability",
                "organization": "Detailed analysis of information organization",
                "examples": {{
                    "good": ["Specific good formatting example 1", "Specific good formatting example 2"],
                    "bad": ["Specific bad formatting example 1", "Specific bad formatting example 2"]
                }}
            }},
            "recommendations": [
                {{
                    "point": "Detailed recommendation",
                    "importance": "Comprehensive explanation of why this is important",
                    "implementation": "Detailed steps for implementation",
                    "impact": "Expected impact of implementing this recommendation",
                    "best_practices": "Industry best practices related to this recommendation"
                }},
                {{
                    "point": "Detailed recommendation",
                    "importance": "Comprehensive explanation of why this is important",
                    "implementation": "Detailed steps for implementation",
                    "impact": "Expected impact of implementing this recommendation",
                    "best_practices": "Industry best practices related to this recommendation"
                }},
                {{
                    "point": "Detailed recommendation",
                    "importance": "Comprehensive explanation of why this is important",
                    "implementation": "Detailed steps for implementation",
                    "impact": "Expected impact of implementing this recommendation",
                    "best_practices": "Industry best practices related to this recommendation"
                }}
            ],
            "market_fit": {{
                "score": "Overall score (0-100)",
                "justification": "Detailed explanation of the score",
                "market_alignment": "Detailed analysis of market alignment",
                "career_trajectory": "Detailed analysis of career trajectory",
                "competitiveness": "Detailed analysis of profile competitiveness",
                "market_trends": "Relevant market trends and requirements"
            }}
        }}

        Ensure each section is comprehensive and detailed, with specific examples and explanations. 
        Focus only on the requested aspects and provide thorough, actionable feedback."""
    
    def _parse_ai_response(self, response: str) -> dict:
        """Parse the AI response into a structured format"""
        try:
            # Parse the JSON response
            parsed_response = json.loads(response)
            
            # Ensure all required sections exist with default empty lists
            default_structure = {
                "skills": {
                    "technical": {"strengths": [], "weaknesses": []},
                    "soft": {"strengths": [], "weaknesses": []}
                },
                "experience": {
                    "achievements": [],
                    "impact": [],
                    "areas_for_improvement": []
                },
                "formatting": {
                    "layout": [],
                    "organization": [],
                    "visual": []
                },
                "overall_score": 0,
                "summary": "No summary available"
            }
            
            # Merge the parsed response with default structure
            for key, value in default_structure.items():
                if key not in parsed_response:
                    parsed_response[key] = value
                elif isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        if subkey not in parsed_response[key]:
                            parsed_response[key][subkey] = subvalue
            
            # Add categories to the response
            parsed_response['categories'] = ANALYSIS_CATEGORIES
            
            return parsed_response
        except json.JSONDecodeError as e:
            print(f"Error parsing AI response: {str(e)}")
            # Return a fallback structure if JSON parsing fails
        return {
                "skills": {
                    "technical": {"strengths": [], "weaknesses": []},
                    "soft": {"strengths": [], "weaknesses": []}
                },
                "experience": {
                    "achievements": [],
                    "impact": [],
                    "areas_for_improvement": []
                },
                "formatting": {
                    "layout": [],
                    "organization": [],
                    "visual": []
                },
                "overall_score": 0,
                "summary": "Error analyzing resume. Please try again.",
            "categories": ANALYSIS_CATEGORIES
        } 