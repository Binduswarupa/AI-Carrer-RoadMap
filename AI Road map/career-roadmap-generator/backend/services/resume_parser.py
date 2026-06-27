"""
Resume Parser Service.
Handles PDF upload, text extraction, and initial skill parsing.
"""
import re
from PyPDF2 import PdfReader
import io


class ResumeParser:
    """Service class for resume parsing and skill extraction."""

    # Common technical skills for keyword matching
    TECH_SKILLS = [
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust',
        'swift', 'kotlin', 'php', 'scala', 'r', 'matlab', 'sql', 'nosql',
        'html', 'css', 'react', 'angular', 'vue', 'svelte', 'next.js', 'node.js',
        'express', 'django', 'flask', 'fastapi', 'spring', 'spring boot',
        'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'terraform',
        'jenkins', 'ci/cd', 'git', 'github', 'gitlab', 'bitbucket',
        'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch', 'cassandra',
        'dynamodb', 'firebase', 'supabase',
        'machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow',
        'pytorch', 'scikit-learn', 'pandas', 'numpy', 'keras',
        'rest api', 'graphql', 'microservices', 'serverless', 'api gateway',
        'linux', 'bash', 'powershell', 'nginx', 'apache',
        'agile', 'scrum', 'jira', 'confluence', 'trello',
        'figma', 'sketch', 'adobe xd', 'photoshop', 'illustrator',
        'tableau', 'power bi', 'data visualization', 'data analysis',
        'blockchain', 'solidity', 'web3', 'ethereum',
        'cybersecurity', 'penetration testing', 'oauth', 'jwt',
        'servicenow', 'salesforce', 'sap', 'oracle',
        'hadoop', 'spark', 'kafka', 'airflow',
        'selenium', 'cypress', 'jest', 'pytest', 'unittest',
        'android', 'ios', 'react native', 'flutter', 'xamarin',
    ]

    SOFT_SKILLS = [
        'leadership', 'communication', 'teamwork', 'problem solving',
        'critical thinking', 'time management', 'adaptability',
        'project management', 'collaboration', 'mentoring',
        'presentation', 'negotiation', 'analytical',
    ]

    def extract_text_from_pdf(self, pdf_file):
        """Extract text content from a PDF file."""
        try:
            if isinstance(pdf_file, bytes):
                pdf_file = io.BytesIO(pdf_file)

            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

            return text.strip()
        except Exception as e:
            raise Exception(f"Failed to parse PDF: {str(e)}")

    def extract_skills(self, text):
        """Extract technical and soft skills from resume text."""
        text_lower = text.lower()
        technical = []
        soft = []

        for skill in self.TECH_SKILLS:
            if skill.lower() in text_lower:
                technical.append(skill.title() if len(skill) > 3 else skill.upper())

        for skill in self.SOFT_SKILLS:
            if skill.lower() in text_lower:
                soft.append(skill.title())

        return {
            'technical': list(set(technical)),
            'soft': list(set(soft))
        }

    def extract_email(self, text):
        """Extract email addresses from text."""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(pattern, text)
        return emails[0] if emails else None

    def extract_phone(self, text):
        """Extract phone numbers from text."""
        pattern = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,15}'
        phones = re.findall(pattern, text)
        return phones[0].strip() if phones else None

    def extract_education(self, text):
        """Extract education-related keywords."""
        education_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'b.tech', 'm.tech',
            'b.e.', 'm.e.', 'bsc', 'msc', 'bca', 'mca', 'mba',
            'b.s.', 'm.s.', 'associate', 'diploma', 'certification',
            'computer science', 'information technology', 'engineering',
            'data science', 'artificial intelligence',
        ]
        text_lower = text.lower()
        found = [kw.title() for kw in education_keywords if kw in text_lower]
        return list(set(found))

    def extract_links(self, text):
        """Extract URLs from text."""
        pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(pattern, text)

    def parse_resume(self, pdf_file):
        """Complete resume parsing pipeline."""
        text = self.extract_text_from_pdf(pdf_file)

        if not text or len(text.strip()) < 50:
            raise Exception("Could not extract sufficient text from PDF. Please ensure the PDF is not image-based.")

        skills = self.extract_skills(text)
        education = self.extract_education(text)
        email = self.extract_email(text)
        phone = self.extract_phone(text)
        links = self.extract_links(text)

        return {
            'raw_text': text,
            'skills': skills,
            'education': education,
            'email': email,
            'phone': phone,
            'links': links,
            'word_count': len(text.split()),
            'character_count': len(text)
        }


# Singleton instance
resume_parser = ResumeParser()
