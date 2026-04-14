# ResumeMatch AI 🤖🚀

ResumeMatch AI is an intelligent resume analysis and role prediction system built on Streamlit. It parses uploaded PDF resumes, evaluates skill alignments using NLP, and provides actionable career feedback, skill gap analysis, and course recommendations automatically. 

## Features

- **PDF Parsing:** Robust text extraction using `pdfplumber`.
- **NLP Analysis & Role Prediction:** Uses `nltk` and `scikit-learn`'s TF-IDF Vectorization combined with cosine similarity logic to classify resumes into fields like Data Science, UI/UX, Cloud DevOps, and Web Development.
- **Smart Scoring Heuristics:** Rates resumes automatically out of 100 based on the density of active technical keywords, project experience hooks, and listed certifications. 
- **Personalized Recommendations:** Offers free external learning resources and YouTube interview prep videos dynamically filtered by your identified career path.
- **Admin Dashboard:** Secure login routes granting access to interactive Pandas and Plotly analytic distributions tracking applicant behavior metrics securely.

## Clean Architecture

The app is decoupled into a robust production-grade structure ensuring simple scalability:

- **/ui:** Responsible purely for rendering Streamlit layout blocks and widgets.
- **/services:** Native python modules containing ML Singleton caching, API connections, database insertions, and stateless logic algorithms to keep the UI layer fast.
- **/data:** Houses JSON and text configurations preventing hard-coded logic clutter.
- **/styles:** Employs centralized adaptive light/dark mode CSS files.

## Local Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SrinivasSurisetti/resume_match_ai.git
   cd resume_match_ai
   ```

2. **Create a Python Virtual Environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Mac/Linux:
   source .venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

4. **Environment Variables:**
   Ensure you establish the follow variables locally (or inside `.streamlit/secrets.toml`):
   - `DATABASE_URL` (Your PostgreSQL connection string)
   - `ADMIN_USERNAME`
   - `ADMIN_PASSWORD`

5. **Run the Application:**
   ```bash
   streamlit run app.py
   ```

## Technical Stack
- **Frontend:** Streamlit 
- **Visualizations:** Plotly Express
- **Machine Learning & NLP:** NLTK, Spacy, scikit-learn
- **Database Engine:** PostgreSQL via psycopg2
