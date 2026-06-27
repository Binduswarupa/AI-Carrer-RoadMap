"""
Groq AI Service Module.
Handles all AI interactions using the Groq API with llama-3.3-70b-versatile model.
"""
import json
from groq import Groq
from config import Config


class GroqService:
    """Service class for Groq AI API interactions."""

    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL

    def _call_groq(self, system_prompt, user_prompt, temperature=0.7, max_tokens=4096):
        """Make a call to Groq API and return the response."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq API error: {e}")
            raise Exception(f"AI service error: {str(e)}")

    def _parse_json_response(self, response_text):
        """Parse JSON from AI response, handling markdown code blocks."""
        cleaned = response_text.strip()
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        return json.loads(cleaned.strip())

    def analyze_resume(self, resume_text):
        """Analyze resume and return structured analysis."""
        system_prompt = """You are an expert ATS resume analyzer and career coach. 
Analyze the provided resume thoroughly and return a JSON response with the following structure:
{
    "ats_score": <number 0-100>,
    "summary": "<brief professional summary>",
    "skills": {
        "technical": ["skill1", "skill2"],
        "soft": ["skill1", "skill2"],
        "tools": ["tool1", "tool2"]
    },
    "education": [{"degree": "", "institution": "", "year": ""}],
    "experience": [{"title": "", "company": "", "duration": "", "highlights": []}],
    "certifications": ["cert1", "cert2"],
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["area1", "area2"],
    "recommendations": ["rec1", "rec2"],
    "keyword_analysis": {
        "present_keywords": ["keyword1"],
        "missing_keywords": ["keyword1"],
        "keyword_density_score": <number 0-100>
    },
    "formatting_score": <number 0-100>,
    "impact_score": <number 0-100>
}
Return ONLY valid JSON. No extra text."""

        user_prompt = f"Analyze this resume:\n\n{resume_text}"
        response = self._call_groq(system_prompt, user_prompt, temperature=0.3, max_tokens=4096)
        return self._parse_json_response(response)

    def analyze_skill_gap(self, current_skills, education, experience, target_role):
        """Identify skill gaps for a target role."""
        system_prompt = """You are a senior career advisor and tech industry expert.
Analyze the skill gap between a candidate's current profile and their target role.
Return a JSON response with this structure:
{
    "target_role": "<role>",
    "overall_readiness": <number 0-100>,
    "missing_skills": {
        "critical": [{"skill": "", "importance": "high/medium", "estimated_learning_time": ""}],
        "recommended": [{"skill": "", "importance": "medium/low", "estimated_learning_time": ""}]
    },
    "missing_certifications": [{"name": "", "provider": "", "priority": "high/medium/low"}],
    "missing_tools": [{"tool": "", "category": "", "alternatives": []}],
    "missing_technologies": [{"tech": "", "category": "", "relevance": ""}],
    "strengths": ["strength1", "strength2"],
    "learning_recommendations": [{"topic": "", "resource_type": "", "priority": ""}],
    "estimated_preparation_time": "",
    "career_path_suggestions": ["path1", "path2"]
}
Return ONLY valid JSON. No extra text."""

        user_prompt = f"""Candidate Profile:
Current Skills: {current_skills}
Education: {education}
Experience: {experience}
Target Role: {target_role}

Identify all skill gaps and provide a comprehensive gap analysis."""

        response = self._call_groq(system_prompt, user_prompt, temperature=0.4, max_tokens=4096)
        return self._parse_json_response(response)

    def generate_roadmap(self, target_role, current_skills, experience_level, timeline="6 months"):
        """Generate a personalized career roadmap."""
        system_prompt = """You are a career planning expert and tech mentor.
Create a detailed, month-by-month career roadmap. Return a JSON response:
{
    "target_role": "<role>",
    "timeline": "<timeline>",
    "experience_level": "<level>",
    "roadmap": [
        {
            "month": 1,
            "title": "Foundation Building",
            "focus_area": "",
            "skills_to_learn": [{"skill": "", "resources": [""], "priority": "high/medium/low"}],
            "certifications": [{"name": "", "provider": "", "duration": ""}],
            "mini_projects": [{"title": "", "description": "", "technologies": []}],
            "practice_platforms": ["platform1"],
            "interview_prep": ["topic1"],
            "milestones": ["milestone1"],
            "weekly_schedule": {
                "week1": "",
                "week2": "",
                "week3": "",
                "week4": ""
            }
        }
    ],
    "overall_tips": ["tip1"],
    "salary_expectations": {"entry": "", "mid": "", "senior": ""},
    "job_market_outlook": ""
}
Create entries for each month of the timeline. Return ONLY valid JSON."""

        user_prompt = f"""Generate a career roadmap:
Target Role: {target_role}
Current Skills: {current_skills}
Experience Level: {experience_level}
Timeline: {timeline}

Create a comprehensive month-by-month roadmap."""

        response = self._call_groq(system_prompt, user_prompt, temperature=0.5, max_tokens=8000)
        return self._parse_json_response(response)

    def recommend_certifications(self, target_role, current_skills, budget="moderate"):
        """Recommend relevant certifications."""
        system_prompt = """You are a certification advisor with deep industry knowledge.
Recommend the most impactful certifications. Return JSON:
{
    "target_role": "<role>",
    "certifications": [
        {
            "name": "",
            "provider": "",
            "category": "cloud/data/ai/devops/security/development",
            "difficulty": "beginner/intermediate/advanced",
            "duration": "",
            "cost": "",
            "benefits": [""],
            "prerequisites": [""],
            "exam_details": "",
            "validity": "",
            "priority": "essential/recommended/nice-to-have",
            "roi_score": <number 1-10>,
            "url": ""
        }
    ],
    "certification_path": ["cert1 -> cert2 -> cert3"],
    "total_estimated_cost": "",
    "total_estimated_time": ""
}
Return ONLY valid JSON."""

        user_prompt = f"""Recommend certifications:
Target Role: {target_role}
Current Skills: {current_skills}
Budget: {budget}

Suggest the most valuable certifications with complete details."""

        response = self._call_groq(system_prompt, user_prompt, temperature=0.4, max_tokens=4096)
        return self._parse_json_response(response)

    def recommend_projects(self, target_role, current_skills, experience_level):
        """Recommend portfolio projects."""
        system_prompt = """You are a tech project mentor and portfolio advisor.
Recommend projects at different difficulty levels. Return JSON:
{
    "target_role": "<role>",
    "projects": {
        "beginner": [
            {
                "title": "",
                "description": "",
                "technologies": [],
                "features": [],
                "duration": "",
                "github_ideas": "",
                "learning_outcomes": [],
                "difficulty_score": <number 1-10>
            }
        ],
        "intermediate": [
            {
                "title": "",
                "description": "",
                "technologies": [],
                "features": [],
                "duration": "",
                "github_ideas": "",
                "learning_outcomes": [],
                "difficulty_score": <number 1-10>
            }
        ],
        "advanced": [
            {
                "title": "",
                "description": "",
                "technologies": [],
                "features": [],
                "duration": "",
                "github_ideas": "",
                "learning_outcomes": [],
                "difficulty_score": <number 1-10>
            }
        ]
    },
    "portfolio_tips": ["tip1"]
}
Return ONLY valid JSON."""

        user_prompt = f"""Recommend projects:
Target Role: {target_role}
Current Skills: {current_skills}
Experience Level: {experience_level}

Suggest 3 projects per difficulty level with full details."""

        response = self._call_groq(system_prompt, user_prompt, temperature=0.6, max_tokens=4096)
        return self._parse_json_response(response)

    def career_prediction(self, skills, education, experience, target_role):
        """Predict career readiness scores."""
        system_prompt = """You are a career analytics expert. Evaluate the candidate's career readiness.
Return JSON:
{
    "employability_score": <number 0-100>,
    "career_readiness_score": <number 0-100>,
    "skill_strength_score": <number 0-100>,
    "scores_breakdown": {
        "technical_skills": <number 0-100>,
        "soft_skills": <number 0-100>,
        "education": <number 0-100>,
        "experience": <number 0-100>,
        "certifications": <number 0-100>,
        "projects": <number 0-100>,
        "market_demand": <number 0-100>
    },
    "strengths": [""],
    "improvement_areas": [""],
    "industry_comparison": "",
    "predicted_salary_range": "",
    "job_readiness_timeline": "",
    "top_matching_roles": [""]
}
Return ONLY valid JSON."""

        user_prompt = f"""Evaluate career readiness:
Skills: {skills}
Education: {education}
Experience: {experience}
Target Role: {target_role}"""

        response = self._call_groq(system_prompt, user_prompt, temperature=0.3, max_tokens=2048)
        return self._parse_json_response(response)

    def learning_resources(self, topic, level="beginner"):
        """Suggest learning resources for a topic."""
        system_prompt = """You are a learning resource curator. Suggest the best free and paid resources.
Return JSON:
{
    "topic": "",
    "level": "",
    "resources": {
        "youtube_channels": [{"name": "", "url": "", "description": ""}],
        "free_courses": [{"name": "", "platform": "", "url": "", "duration": ""}],
        "documentation": [{"name": "", "url": "", "description": ""}],
        "practice_websites": [{"name": "", "url": "", "focus": ""}],
        "books": [{"title": "", "author": "", "level": ""}],
        "communities": [{"name": "", "platform": "", "url": ""}]
    }
}
Return ONLY valid JSON."""

        user_prompt = f"Suggest learning resources for: {topic} at {level} level."
        response = self._call_groq(system_prompt, user_prompt, temperature=0.5, max_tokens=2048)
        return self._parse_json_response(response)

    def career_chat(self, message, context=""):
        """AI Career Mentor chatbot response."""
        system_prompt = """You are an expert AI Career Mentor. You provide:
- Career guidance and advice
- Interview tips and preparation strategies
- Certification recommendations
- Learning path suggestions
- Resume improvement tips
- Industry insights and trends
- Salary negotiation advice
- Job search strategies

Be helpful, encouraging, and specific. Provide actionable advice.
Keep responses concise but informative. Use bullet points when listing items.
If asked about something outside your expertise, guide the conversation back to career topics."""

        user_prompt = message
        if context:
            user_prompt = f"Context: {context}\n\nUser Question: {message}"

        response = self._call_groq(system_prompt, user_prompt, temperature=0.7, max_tokens=2048)
        return response

    def generate_interview_questions(self, role, difficulty="mixed"):
        """Generate interview questions for a role."""
        system_prompt = """You are a senior technical interviewer. Generate interview questions.
Return JSON:
{
    "role": "",
    "questions": {
        "technical": [{"question": "", "difficulty": "", "expected_answer_points": []}],
        "behavioral": [{"question": "", "tip": ""}],
        "system_design": [{"question": "", "key_topics": []}],
        "coding": [{"question": "", "difficulty": "", "concepts": []}]
    },
    "preparation_tips": [""]
}
Return ONLY valid JSON."""

        user_prompt = f"Generate interview questions for: {role} (Difficulty: {difficulty})"
        response = self._call_groq(system_prompt, user_prompt, temperature=0.6, max_tokens=4096)
        return self._parse_json_response(response)


# Singleton instance
groq_service = GroqService()
