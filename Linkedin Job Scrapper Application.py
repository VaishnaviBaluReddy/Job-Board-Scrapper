import matplotlib
matplotlib.use('agg')  # Use for non-interactive backend


import requests
from bs4 import BeautifulSoup
import cohere
import pandas as pd
import time
import os
import io
from datetime import datetime
from collections import Counter
from flask import Flask, request, render_template, send_file
import matplotlib.pyplot as plt
import base64

# Initialize Flask app
linkedin_scrapper_app = Flask(__name__)

# Cohere API Client
co = cohere.Client(api_key="your-api-key")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0'
}

# Keep your original working functions
def map_experience_level(yoe: int) -> str:
    if yoe <= 0:
        return "Internship"
    elif yoe <= 2:
        return "Entry level"
    elif yoe <= 5:
        return "Associate"
    elif yoe <= 8:
        return "Mid-Senior"
    elif yoe <= 12:
        return "Director"
    else:
        return "Executive"

def extract_skills_llm(jd_text):
    try:
        prompt = f"""
        Extract only technical and professional skills from the job description provided below.
        - Return ONLY a comma-separated list of technical skills, with no additional text or formatting.
        - Do NOT include soft skills, vague phrases, behavioral traits, or repetitive entries.
        - Focus on extracting only actionable, technical, and role-specific skills (e.g., Python, SQL, TensorFlow, Cloud Computing).
        - Avoid adding commentary, instructions, or any extra information beyond the comma-separated list.

        Job Description:
        {jd_text}
        """
        
        response = co.chat(model="command", message=prompt)
        skills = response.text.strip()
        
        skills = [s.strip() for s in skills.split(',')]
        skills = list(set(skill for skill in skills if len(skill) > 1 and not any(c in skill.lower() for c in ["let me", "vague", "repetitive", "commentary", "instructions"])))
        
        return ' | '.join(sorted(skills))
    except Exception as e:
        print(f"Error calling Cohere API: {e}")
        return ""

def scrape_job_description(jd_url: str) -> str:
    try:
        time.sleep(2)
        session = requests.Session()
        response = session.get(jd_url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Failed to fetch page: {response.status_code}")
            return ""

        soup = BeautifulSoup(response.text, 'html.parser')
        
        selectors = [
            ('div', {'class': 'jobs-description__content jobs-description-content jobs-description__content--condensed'}),
            ('div', {'class': 'jobs-description__content jobs-description-content'}),
            ('div', {'id': 'job-details'}),
            ('div', {'class': 'jobs-box__html-content'}),
            ('div', {'class': 'description__text'}),
            ('section', {'class': 'description'})
        ]
        
        jd_text = ""
        for tag, attrs in selectors:
            section = soup.find(tag, attrs)
            if section:
                print(f"Found content using selector: {tag}, {attrs}")
                jd_text = section.get_text(separator=" ", strip=True)
                break
        
        if not jd_text:
            job_divs = soup.find_all('div', class_=lambda x: x and 'job' in x.lower())
            if job_divs:
                longest_text = ""
                for div in job_divs:
                    text = div.get_text(separator=" ", strip=True)
                    if len(text) > len(longest_text):
                        longest_text = text
                jd_text = longest_text
                print("Found content using fallback method")
        
        if jd_text and len(jd_text) > 100:
            return jd_text
        else:
            print("Found text too short to be a job description")
            return ""
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        return ""

def scrape_linkedin(role: str, location: str, yoe: int) -> pd.DataFrame:
    url = f"https://www.linkedin.com/jobs/search?keywords={role.replace(' ', '%20')}&location={location.replace(' ', '%20')}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    jobs = []
    for job_card in soup.find_all('div', class_='base-card'):
        title = job_card.find('h3', class_='base-search-card__title')
        title = title.text.strip() if title else "N/A"

        company = job_card.find('h4', class_='base-search-card__subtitle')
        company = company.text.strip() if company else "N/A"

        loc = job_card.find('span', class_='job-search-card__location')
        loc = loc.text.strip() if loc else "N/A"

        jd_link = job_card.find('a', class_='base-card__full-link')
        jd_link = jd_link['href'] if jd_link else "N/A"
        print(jd_link)

        jobs.append({
            'Role': title,
            'Company': company,
            'Location': loc,
            'Experience Level': map_experience_level(yoe),
            'JD Link': jd_link
        })
    
    return pd.DataFrame(jobs)

def process_jobs(jobs_df: pd.DataFrame) -> pd.DataFrame:
    if 'Required Skills' not in jobs_df.columns:
        jobs_df['Required Skills'] = ""
    
    print("\nProcessing job listings...")
    for index, job in jobs_df.iterrows():
        print(f"Processing job {index + 1}/{len(jobs_df)}")

        if job['JD Link'] != "N/A":
            jd_text = scrape_job_description(job['JD Link'])
            if jd_text:
                print(f"Extracting skills for job: {job['Role']}")
                skills = extract_skills_llm(jd_text)
                if skills:
                    jobs_df.at[index, 'Required Skills'] = skills
                else:
                    print(f"No skills found for job: {job['Role']}")
    
    # Save to CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"job_listings_{timestamp}.csv"
    os.makedirs('static/downloads', exist_ok=True)
    jobs_df.to_csv(f"static/downloads/{filename}", index=False, encoding='utf-8-sig')
    print(f"Updated job listings saved to {filename}")
    
    return jobs_df, filename

def generate_visualizations(jobs_df: pd.DataFrame, role: str, location: str, yoe: int):
    if 'Required Skills' not in jobs_df.columns or jobs_df['Required Skills'].isna().all():
        return None, None

    all_skills = []
    for skills in jobs_df['Required Skills'].dropna():
        all_skills.extend(skills.split(' | '))

    if not all_skills:
        return None, None

    skill_counts = Counter(all_skills)
    total_skills = sum(skill_counts.values())
    top_skills = skill_counts.most_common(25)
    skill_names, skill_values = zip(*top_skills)

    date = datetime.now().strftime('%Y-%m-%d')

    # Set custom color palette and font
    plt.rcParams.update({
        "font.family": "monospace",
        "axes.facecolor": "#222629",
        "axes.edgecolor": "#c5c697",
        "axes.labelcolor": "#c5c697",
        "xtick.color": "#c5c697",
        "ytick.color": "#c5c697",
        "figure.facecolor": "#0b0c10",
        "text.color": "#c5c697",
    })

    # Create pie chart
    plt.figure(figsize=(7, 6))  # Reduced size
    colors = plt.cm.tab20.colors[:len(skill_values)]
    plt.pie(
        skill_values,
        labels=skill_names,
        startangle=140,
        colors=colors,
    )
    plt.title(f"Top Skills Distribution for {role} in {location}\n({map_experience_level(yoe)} Level) as of {date}")
    pie_img = io.BytesIO()
    plt.savefig(pie_img, format='png', bbox_inches='tight', dpi=200)  # Reduced DPI for smaller files
    pie_img.seek(0)
    plt.close()

    # Create bar chart
    plt.figure(figsize=(8, 6))  # Reduced width
    plt.barh(skill_names, skill_values, color=colors)
    plt.xlabel('Number of Occurrences')
    plt.ylabel('Skills')
    plt.title(f"Top Skills Distribution for {role} in {location}\n({map_experience_level(yoe)} Level) as of {date}")
    plt.gca().invert_yaxis()

    # Add percentage labels at the end of bars
    for i, (value, name) in enumerate(zip(skill_values, skill_names)):
        percentage = (value / total_skills) * 100
        plt.text(value + 0.5, i, f"{percentage:.1f}%", va='center', color="#c5c697")

    bar_img = io.BytesIO()
    plt.savefig(bar_img, format='png', bbox_inches='tight', dpi=200)  # Reduced DPI for smaller files
    bar_img.seek(0)
    plt.close()

    pie_base64 = base64.b64encode(pie_img.getvalue()).decode()
    bar_base64 = base64.b64encode(bar_img.getvalue()).decode()

    return pie_base64, bar_base64


@linkedin_scrapper_app.route('/')
def index():
    return render_template('index.html')

@linkedin_scrapper_app.route('/process', methods=['POST'])
def process():
    try:
        role = request.form.get('role', '')
        location = request.form.get('location', '')
        yoe = int(request.form.get('yoe', 0))

        # Scrape LinkedIn jobs
        jobs_df = scrape_linkedin(role, location, yoe)

        if not jobs_df.empty:
            # Process jobs and prepare filename
            jobs_df, filename = process_jobs(jobs_df)

            # Ensure the 'Link' column is included and valid
            if 'Link' not in jobs_df.columns:
                jobs_df['Link'] = 'N/A'

            # Generate visualizations
            pie_chart, bar_chart = generate_visualizations(jobs_df, role, location, yoe)

            return render_template(
                'results.html',
                pie_chart=pie_chart,
                bar_chart=bar_chart,
                filename=filename,
                jobs=jobs_df.to_dict('records')
            )
        else:
            return "No jobs found", 404

    except Exception as e:
        print(f"Error processing request: {e}")
        return f"An error occurred: {str(e)}", 500


@linkedin_scrapper_app.route('/download/<filename>')
def download_results(filename):
    try:
        return send_file(
            f'static/downloads/{filename}',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return f"File not found: {str(e)}", 404

if __name__ == '__main__':
    linkedin_scrapper_app.run(debug=True)