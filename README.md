# Job Insights and Analytics App

A dynamic and scalable Flask-based web application that empowers users with actionable insights into the job market. Designed for working professionals and job seekers, it provides a data-driven approach to identifying in-demand skills and career opportunities. With robust scraping, analysis, and visualization features,  extracts and processes job descriptions from LinkedIn to highlight the most sought-after technical skills.

The application is modular and extensible, with plans to incorporate other job portals, making it a comprehensive tool for understanding job trends across platforms.

The result looks something like this: 
**Front Page**:
![Front page](https://github.com/user-attachments/assets/4eeb965a-a7cc-4dc1-97ff-7ee024ee5579)
**Results**:
![Charts](https://github.com/user-attachments/assets/0278d60e-b48d-4cc4-8a20-ba44719e81f5)
![Job listings](https://github.com/user-attachments/assets/6ffdd4ca-50e3-4a9c-b820-2df6c3b42939)



Key Features
### Job Scraping:
- Retrieve job listings from LinkedIn based on user-defined criteria such as job role, location, and years of experience (YOE).
### Skills Extraction:
- Extract actionable technical and professional skills from job descriptions using advanced NLP models.
- Focus solely on role-specific, technical skills (e.g., Python, SQL, TensorFlow).
### Data Visualization:
- Generate clear and interactive visualizations, including:
- Bar Charts: Show the frequency of top technical skills.
- Pie Charts: Display skill distributions for better insights.
### Dynamic Processing:
- Tailor job results based on user inputs like experience levels (Internship, Entry-Level, Associate, etc.).
### Downloadable Outputs:
- Save processed job listings and extracted skills as downloadable CSV files.
### Scalability:
- Designed to expand beyond LinkedIn, integrating other job portals like Indeed, Glassdoor, etc., in the future.

## How It Works
### Workflow
- **Input Details:**
Users provide the role, location, and years of experience via the web interface.

- **Scraping:**
The app fetches job listings from LinkedIn using BeautifulSoup and organizes the data.

- **Skills Extraction:**
Job descriptions are processed through NLP models to extract the most relevant skills.

- **Processing:**
The app processes the scraped data to add skills information, map experience levels, and refine the listings.

- **Visualization:**
Top skills are visualized through bar and pie charts.

- **Output:**
Users can download job listings and skills data as CSV files.

## Setup Guide
### Prerequisites
Python Environment:

Ensure Python 3.8+ is installed.
Libraries: Install the required Python libraries using 
    
    pip install -r requirements.txt.

### Steps to Run the App 

Set up your Cohere API key in the code:
Replace api_key="YOUR_API_KEY" in the extract_skills_llm function.

### Run the Flask application:

    python app.py  

### Open the app in your browser: 
Navigate to http://127.0.0.1:5000 in your web browser.

## Folder Structure


    /Project_name
    ├── static/  
    │   ├── visualizations/   # Directory for saved visualizations  
    ├── templates/  
    │   ├── index.html        # Landing page for user inputs  
    │   ├── results.html      # Results page with visualizations  
    ├── app.py                # Main Flask app  
    ├── requirements.txt      # Dependencies  
    ├── README.md             # Documentation  

# Core Functionalities
### Job Scraping
The scrape_linkedin function gathers job listings from LinkedIn using specified parameters.

### Skills Extraction
The extract_skills_llm function leverages an NLP model to process job descriptions and extract technical skills.

### Visualization
The generate_visualizations function creates bar and pie charts of the most common skills.

### File Management
CSV files for job listings and skills are dynamically named and saved.

# Future Plans
### Integration with Additional Job Portals:
- Extend support to platforms like Indeed, and Naukri.
### Advanced Analytics:
- Add predictive insights, such as demand trends for skills and roles.
### Personalized Recommendations:
- Provide users with tailored career advice based on skills gap analysis.

## Contributions

Contributions are welcome! If you'd like to add features or suggest improvements, feel free to open an issue or submit a pull request.

## Contact

For questions or feedback, please reach out to vaishnavibalureddy2@gmail.com.
