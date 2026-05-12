"""
Salary Predictor Module
Uses OpenAI to predict salary ranges based on job details and market data
"""

import openai
import re


class SalaryPredictor:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = api_key

    def predict_salary(self, job_title, company, location, job_description):
        """
        Use OpenAI to predict salary range based on job details
        Returns min, max, and average salary
        """
        try:
            prompt = f"""As a salary research expert, estimate the salary range for the following position based on current market data:

Job Title: {job_title}
Company: {company}
Location: {location}
Job Description: {job_description[:1000]}

Provide a realistic salary range in USD considering:
- Industry standards
- Location cost of living
- Required experience and skills
- Company size and type

Respond in this format:
MINIMUM_SALARY: [number]
MAXIMUM_SALARY: [number]
AVERAGE_SALARY: [number]
EXPLANATION: [brief justification]
"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a salary research expert with access to current market data."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )

            analysis = response.choices[0].message.content

            salary_min = self._extract_salary(analysis, "MINIMUM_SALARY")
            salary_max = self._extract_salary(analysis, "MAXIMUM_SALARY")
            salary_avg = self._extract_salary(analysis, "AVERAGE_SALARY")

            if salary_avg == 0:
                salary_avg = (salary_min + salary_max) // 2

            if salary_min == 0 and salary_max == 0 and salary_avg == 0:
                return self._get_default_salary(job_title)

            return {
                'min': salary_min,
                'max': salary_max,
                'avg': salary_avg,
                'explanation': analysis
            }

        except Exception as e:
            print(f"Error in salary prediction: {str(e)}")
            return self._get_default_salary(job_title)

    def _extract_salary(self, text, salary_type):
        """Extract salary value from analysis text"""
        try:
            pattern = f"{salary_type}:\\s*\\$?([0-9,]+)"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                salary_str = match.group(1).replace(',', '')
                return int(salary_str)
            return 0
        except:
            return 0

    def _get_default_salary(self, job_title):
        """Return default salary estimates based on job title keywords"""
        title_lower = job_title.lower()

        salary_ranges = {
            'senior': (120000, 180000, 150000),
            'lead': (130000, 190000, 160000),
            'principal': (150000, 220000, 185000),
            'staff': (140000, 200000, 170000),
            'manager': (110000, 170000, 140000),
            'director': (150000, 250000, 200000),
            'engineer': (80000, 140000, 110000),
            'developer': (75000, 135000, 105000),
            'scientist': (90000, 150000, 120000),
            'analyst': (65000, 110000, 87500),
            'architect': (120000, 180000, 150000),
            'consultant': (85000, 145000, 115000),
            'intern': (40000, 70000, 55000),
            'junior': (60000, 90000, 75000),
            'entry': (55000, 85000, 70000),
        }

        for keyword, (min_sal, max_sal, avg_sal) in salary_ranges.items():
            if keyword in title_lower:
                return {
                    'min': min_sal,
                    'max': max_sal,
                    'avg': avg_sal,
                    'explanation': f"Estimated based on market data for {job_title}"
                }

        return {
            'min': 70000,
            'max': 120000,
            'avg': 95000,
            'explanation': f"General estimate for {job_title}"
        }
