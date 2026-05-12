"""
Resume Matcher Module
Uses OpenAI GPT to match resume with job descriptions
"""

import openai
import re


class ResumeMatcher:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = api_key

    def match_resume_to_job(self, resume_text, job_description):
        """
        Use OpenAI to analyze resume match with job description
        Returns match percentage and details
        """
        try:
            prompt = f"""You are an expert resume analyzer. Compare the following resume with the job description and provide:
1. A match percentage (0-100)
2. Key matching skills and experiences
3. Missing qualifications
4. Recommendations

Resume:
{resume_text[:3000]}

Job Description:
{job_description[:2000]}

Provide your analysis in the following format:
MATCH_PERCENTAGE: [number between 0-100]
MATCHING_SKILLS: [list key matching points]
MISSING_QUALIFICATIONS: [list gaps]
RECOMMENDATIONS: [brief suggestions]
"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert resume and job matching analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )

            analysis = response.choices[0].message.content

            match_percentage = self._extract_match_percentage(analysis)

            return {
                'match_percentage': match_percentage,
                'details': analysis
            }

        except Exception as e:
            print(f"Error in resume matching: {str(e)}")
            return {
                'match_percentage': 50,
                'details': f"Unable to perform detailed analysis. Error: {str(e)}\n\nPlease check your OpenAI API key."
            }

    def _extract_match_percentage(self, analysis_text):
        """Extract match percentage from analysis"""
        try:
            match = re.search(r'MATCH_PERCENTAGE:\s*(\d+)', analysis_text)
            if match:
                percentage = int(match.group(1))
                return min(100, max(0, percentage))

            match = re.search(r'(\d+)%', analysis_text)
            if match:
                percentage = int(match.group(1))
                return min(100, max(0, percentage))

            return 50

        except:
            return 50
