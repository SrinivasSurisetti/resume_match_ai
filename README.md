# ResumeMatch AI 🤖🚀

ResumeMatch AI is an AI-powered resume analysis and role prediction system that evaluates resumes against industry skill requirements, identifies skill gaps, and provides personalized learning recommendations to improve job readiness.

## 🎯 Problem Statement

Most resumes fail to match job requirements due to missing or poorly structured skills. This system bridges that gap by analyzing resumes and providing actionable feedback.

## 💡 Solution

ResumeMatch AI automatically extracts resume content, predicts the most suitable job role, evaluates skill alignment, and suggests improvements and learning resources.

## Features

- 📄 Resume Parsing using pdfplumber
- 🧠 Role Prediction using TF-IDF + Cosine Similarity
- 📊 Resume Scoring (0–100) based on skill density
- 📉 Skill Gap Analysis for target roles
- 🎯 Personalized Course Recommendations
- 🔐 Admin Dashboard with analytics (Plotly + Pandas)


## 📸 Screenshots

### 🏠 Home Interface
Main landing page for resume upload and analysis.
<img width="1897" height="894" alt="Screenshot 2026-04-14 160752" src="https://github.com/user-attachments/assets/2c1fd57a-2d4e-40ea-84cb-4192b482382f" />


### 📄 Resume Upload & Preview
Upload and preview PDF resumes for analysis.
<img width="1880" height="895" alt="Screenshot 2026-04-14 160906" src="https://github.com/user-attachments/assets/22351577-e4af-4832-98a4-701f870aa6c3" />


### 📊 Prediction & Skill Analysis
Displays predicted role, confidence score, and missing skills.
<img width="1889" height="833" alt="Screenshot 2026-04-14 160933" src="https://github.com/user-attachments/assets/4fc2d5c3-cf82-4e42-8711-359f7d9bdb56" />

### 🛠️ Admin Dashboard
Visualizes user data, role distribution, and resume analytics.
<img width="1862" height="851" alt="Screenshot 2026-04-14 161037" src="https://github.com/user-attachments/assets/b01d709f-6cbf-4fad-b638-8398eea0e608" />

## 🚀 Highlights

- Built with clean modular architecture (UI + Services separation)
- Integrated NLP + ML techniques for role prediction
- Real-time resume analysis with dynamic UI feedback
- Cloud-ready PostgreSQL integration (NeonDB)

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


## 🛠 Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python
- **ML/NLP:** Scikit-learn, NLTK, SpaCy
- **Database:** PostgreSQL (NeonDB)
- **Visualization:** Plotly

## 🔮 Future Improvements

- Replace TF-IDF with transformer-based models (BERT)
- Add resume-job matching using embeddings
- Deploy as a full web app (React + FastAPI)
- Add user authentication system
