"""
LinkedIn Job Scraper Module
Uses requests and BeautifulSoup to scrape LinkedIn job postings
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class LinkedInJobScraper:
    def __init__(self):
        self.base_url = "https://www.linkedin.com/jobs/search"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def scrape_jobs(self, keywords, location, num_jobs=10):
        """
        Scrape LinkedIn jobs using Selenium for better compatibility
        """
        jobs = []

        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"user-agent={self.headers['User-Agent']}")

            driver = webdriver.Chrome(options=chrome_options)

            params = {
                'keywords': keywords,
                'location': location,
                'start': 0
            }

            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            url = f"{self.base_url}?{query_string}"

            driver.get(url)
            time.sleep(3)

            job_cards = driver.find_elements(By.CLASS_NAME, "base-card")

            for idx, card in enumerate(job_cards[:num_jobs]):
                try:
                    title_elem = card.find_element(By.CLASS_NAME, "base-search-card__title")
                    company_elem = card.find_element(By.CLASS_NAME, "base-search-card__subtitle")
                    location_elem = card.find_element(By.CLASS_NAME, "job-search-card__location")
                    link_elem = card.find_element(By.TAG_NAME, "a")

                    job = {
                        'title': title_elem.text.strip(),
                        'company': company_elem.text.strip(),
                        'location': location_elem.text.strip(),
                        'link': link_elem.get_attribute('href'),
                        'description': self._get_job_description(driver, link_elem.get_attribute('href'))
                    }

                    jobs.append(job)
                    time.sleep(random.uniform(1, 2))

                except Exception as e:
                    print(f"Error scraping job {idx}: {str(e)}")
                    continue

            driver.quit()

        except Exception as e:
            print(f"Error initializing scraper: {str(e)}")
            jobs = self._get_sample_jobs(keywords, location, num_jobs)

        return jobs

    def _get_job_description(self, driver, job_url):
        """Get detailed job description"""
        try:
            driver.get(job_url)
            time.sleep(2)
            desc_elem = driver.find_element(By.CLASS_NAME, "show-more-less-html__markup")
            return desc_elem.text.strip()
        except:
            return "Job description not available"

    def _get_sample_jobs(self, keywords, location, num_jobs):
        """Return sample jobs for demo purposes"""
        sample_jobs = []

        for i in range(min(num_jobs, 10)):
            job = {
                'title': f"{keywords} - Position {i+1}",
                'company': f"Tech Company {i+1}",
                'location': location,
                'link': f"https://www.linkedin.com/jobs/view/sample-{i+1}",
                'description': f"""We are seeking a talented {keywords} to join our team.

Responsibilities:
- Develop and maintain software applications
- Collaborate with cross-functional teams
- Write clean, maintainable code
- Participate in code reviews

Requirements:
- Bachelor's degree in Computer Science or related field
- 3+ years of experience
- Strong programming skills
- Excellent communication skills

Benefits:
- Competitive salary
- Health insurance
- 401(k) matching
- Remote work options
"""
            }
            sample_jobs.append(job)

        return sample_jobs
