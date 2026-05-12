import streamlit as st
import streamlit as st
import pandas as pd
from datetime import datetime
from scraper import LinkedInJobScraper
from resume_matcher import ResumeMatcher
from salary_predictor import SalaryPredictor

st.set_page_config(page_title="LinkedIn Job Hunter", page_icon="🎯", layout="wide")

def load_config():
    """Initialize session state variables"""
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = ""
    if "jobs_data" not in st.session_state:
        st.session_state.jobs_data = []

def save_results(jobs_df):
    """Save filtered job results to CSV file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"job_results_{timestamp}.csv"
    jobs_df.to_csv(filename, index=False)
    return filename

def main():
    load_config()
    st.title("🎯 LinkedIn Job Hunter")
    st.markdown("---")

    with st.sidebar:
        st.header("⚙️ Configuration")
        openai_api_key = st.text_input(
            "OpenAI API Key", 
            value=st.session_state.openai_api_key, 
            type="password"
        )
        if openai_api_key:
            st.session_state.openai_api_key = openai_api_key

        st.markdown("---")
        st.header("📄 Resume")
        resume_file = st.file_uploader(
            "Upload your resume (PDF/TXT)", 
            type=["pdf", "txt"]
        )

        st.markdown("---")
        st.header("🔍 Filters")
        min_match_percentage = st.slider("Minimum Match %", 0, 100, 50, 5)
        min_salary = st.number_input("Minimum Expected Salary ($)", 0, step=5000)
        max_salary = st.number_input(
            "Maximum Expected Salary ($)", 
            0, 
            value=300000, 
            step=5000
        )

    col1, col2 = st.columns([2, 1])
    with col1:
        st.header("🔎 Job Search")
        search_query = st.text_input(
            "Job Title / Keywords", 
            placeholder="e.g., Software Engineer"
        )
    with col2:
        st.header("📍 Location")
        location = st.text_input(
            "Location", 
            placeholder="e.g., United States, Remote"
        )

    col3, col4, col5 = st.columns([1, 1, 2])
    with col3:
        num_jobs = st.number_input("Number of Jobs", 1, 100, 10)
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        search_button = st.button(
            "🚀 Search Jobs",
            type="primary", 
            use_container_width=True
        )

    st.markdown("---")

    if search_button:
        if not st.session_state.openai_api_key:
            st.error("⚠️ Please enter your OpenAI API key")
            return
        if not resume_file:
            st.error("⚠️ Please upload your resume")
            return
        if not search_query:
            st.error("⚠️ Please enter a job title")
            return

        with st.spinner("📄 Processing resume..."):
            resume_text = ""
            if resume_file.type == "application/pdf":
                import PyPDF2
                import io
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(resume_file.read()))
                for page in pdf_reader.pages:
                    resume_text += page.extract_text()
            else:
                resume_text = resume_file.read().decode("utf-8")

        scraper = LinkedInJobScraper()
        matcher = ResumeMatcher(st.session_state.openai_api_key)
        salary_predictor = SalaryPredictor(st.session_state.openai_api_key)

        with st.spinner(f"🔍 Scraping {num_jobs} jobs..."):
            jobs = scraper.scrape_jobs(search_query, location, num_jobs)
            st.success(f"✅ Found {len(jobs)} jobs")

        if not jobs:
            st.warning("No jobs found")
            return

        progress_bar = st.progress(0)
        status_text = st.empty()
        processed_jobs = []

        for idx, job in enumerate(jobs):
            status_text.text(f"Processing {idx + 1}/{len(jobs)}: {job['title']}")
            match_result = matcher.match_resume_to_job(resume_text, job["description"])
            salary_range = salary_predictor.predict_salary(
                job["title"], 
                job["company"], 
                location, 
                job["description"]
            )

            processed_job = {
                "title": job["title"], 
                "company": job["company"], 
                "location": job["location"],
                "description": job["description"], 
                "link": job["link"],
                "match_percentage": match_result["match_percentage"], 
                "match_details": match_result["details"],
                "salary_min": salary_range["min"], 
                "salary_max": salary_range["max"], 
                "salary_avg": salary_range["avg"]
            }
            processed_jobs.append(processed_job)
            progress_bar.progress((idx + 1) / len(jobs))

        status_text.text("✅ Complete!")
        progress_bar.empty()
        status_text.empty()
        st.session_state.jobs_data = processed_jobs

    if st.session_state.jobs_data:
        st.header("📊 Job Results")
        jobs_df = pd.DataFrame(st.session_state.jobs_data)
        filtered_df = jobs_df[
            (jobs_df["match_percentage"] >= min_match_percentage) & 
            (jobs_df["salary_avg"] >= min_salary) & 
            (jobs_df["salary_avg"] <= max_salary)
        ]

        st.subheader(f"Showing {len(filtered_df)} jobs (from {len(jobs_df)} total)")

        if len(filtered_df) == 0:
            st.warning("No jobs match filters")
            return

        filtered_df = filtered_df.sort_values("match_percentage", ascending=False)

        col_d1, col_d2 = st.columns([3, 1])
        with col_d2:
            if st.button("💾 Export CSV"):
                filename = save_results(filtered_df)
                st.success(f"Saved to {filename}")

        for idx, job in filtered_df.iterrows():
            with st.container():
                col_left, col_right = st.columns([3, 1])
                with col_left:
                    st.markdown(f"### [{job['title']}]({job['link']})")
                    st.markdown(f"**{job['company']}** • {job['location']}")
                with col_right:
                    match_pct = job["match_percentage"]
                    color = "green" if match_pct >= 80 else "orange" if match_pct >= 60 else "red"
                    st.markdown(
                        f"<h2 style='color: {color}; text-align: center;'>{match_pct}%</h2>", 
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        "<p style='text-align: center;'>Match</p>", 
                        unsafe_allow_html=True
                    )

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Min Salary", f"${job['salary_min']:,.0f}")
                with c2:
                    st.metric("Expected", f"${job['salary_avg']:,.0f}")
                with c3:
                    st.metric("Max Salary", f"${job['salary_max']:,.0f}")

                with st.expander("📋 Details"):
                    st.markdown("**Match Analysis:**")
                    st.markdown(job["match_details"])
                    st.markdown("---")
                    st.markdown("**Job Description:**")
                    desc = job["description"]
                    st.markdown(desc[:500] + "..." if len(desc) > 500 else desc)
                st.markdown("---")

if __name__ == "__main__":
    main()
