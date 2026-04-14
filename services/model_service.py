import re
import json
import logging
from difflib import get_close_matches
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config import JOB_ROLES_FILE

logger = logging.getLogger(__name__)

class ModelService:
    _instance = None
    _job_roles = None
    _tfidf = None
    _vectors = None
    _role_index = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelService, cls).__new__(cls)
            cls._instance._job_roles = cls._instance._load_job_roles()
            cls._instance._initialize_models()
        return cls._instance

    def _load_job_roles(self):
        """Loads the predefined JSON string of job roles for ML training mapping."""
        try:
            with open(JOB_ROLES_FILE, 'r', encoding='utf-8') as f:
                logger.info(f"Loaded Job Roles from {JOB_ROLES_FILE}")
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load job roles from {JOB_ROLES_FILE}: {e}")
            return {
                'Data Science': ['python machine learning deep learning pandas numpy statistics nlp'],
                'Web Development': ['html css javascript react node django flask typescript php'],
                'Mobile Development': ['kotlin java android ios swift flutter react native'],
                'UI/UX Design': ['ux ui figma adobe xd wireframe prototype user research'],
                'Cloud / DevOps': ['aws azure gcp docker kubernetes terraform ci/cd devops'],
                'Data Engineering': ['sql spark hadoop etl airflow bigquery redshift data pipeline']
            }

    def _initialize_models(self):
        """Pre-computes the TF-IDF vectors for the predefined roles so it only runs once per server uptime."""
        texts = []
        self._role_index = []
        for role, samples in self._job_roles.items():
            for sample in samples:
                texts.append(sample)
                self._role_index.append(role)
        
        self._tfidf = TfidfVectorizer(stop_words='english')
        self._vectors = self._tfidf.fit_transform(texts)
        logger.info("Initialized ML predictive models globally.")

    def predict_role(self, resume_text):
        """Measures cosine similarity between text extracted and JSON profiles."""
        if not resume_text:
            return 'General Technology', 0.0

        try:
            input_vector = self._tfidf.transform([resume_text])
            similarity = cosine_similarity(input_vector, self._vectors).flatten()
            
            best_idx = int(similarity.argmax())
            best_role = self._role_index[best_idx]
            confidence = float(similarity[best_idx])

            return best_role, confidence
        except Exception as e:
            logger.error(f"Failed to predict role for resume text: {e}")
            return 'General Technology', 0.0

    def calculate_smart_score(self, text, skills):
        """Determines holistic Resume match heuristic score out of 100."""
        # Using simple normalization matching logic mapped locally avoiding parser_service cyclic dependency
        normalized_text = text.lower()
        normalized_text = re.sub(r'[^a-z0-9+#]+', ' ', normalized_text)
        
        skill_count = min(len(skills), 12)
        skill_score = skill_count * 5

        project_count = len(re.findall(r'\bprojects?\b', normalized_text))
        project_score = min(project_count, 3) * 10

        experience_score = 20 if 'experience' in normalized_text else 0

        certification_count = len(re.findall(r'\b(certification|certifications|certified|certificate)\b', normalized_text))
        certification_score = min(certification_count, 2) * 10

        score = skill_score + project_score + experience_score + certification_score
        score = min(score, 100)

        if score < 40:
            category = 'Weak'
        elif score < 70:
            category = 'Moderate'
        else:
            category = 'Strong'

        return score, category

    def generate_resume_feedback(self, text, skills, score):
        """Provides actionable feedback strings to improve logic."""
        normalized_text = text.lower()
        normalized_text = re.sub(r'[^a-z0-9+#]+', ' ', normalized_text)
        suggestions = []

        if not re.search(r'\bprojects?\b', normalized_text):
            suggestions.append("Add a dedicated projects section with measurable achievements.")
        if not re.search(r'\bexperience\b', normalized_text):
            suggestions.append("Add an experience section describing your work history and impact.")
        if not re.search(r'\b(certification|certifications|certified|certificate)\b', normalized_text):
            suggestions.append("Include certifications or training to boost credibility.")
        if len(skills) < 5:
            suggestions.append("Expand the skills section with more relevant technical keywords.")
        if not re.search(r'\b(achievements|awards|recognition|delivered|launched|improved|optimized)\b', normalized_text):
            suggestions.append("Include measurable achievements or outcomes for each role/project.")
        if score < 40 and "Add a dedicated projects section" not in suggestions:
            suggestions.append("Add more project details and examples of results to strengthen the resume.")
        if score < 70 and len(suggestions) < 5:
            suggestions.append("Use active metrics and outcomes to make your resume more compelling.")

        # Deduplicate while preserving order
        unique_suggestions = list(dict.fromkeys(suggestions))
        return unique_suggestions[:5]

    def _normalize_skill_local(self, skill):
        clean = skill.lower().strip()
        clean = re.sub(r'[^a-z0-9+#]+', ' ', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

    def find_missing_skills(self, user_skills, role):
        """Identifies any gaps based on the role requested and outputs the explicit strings."""
        if not role or role not in self._job_roles:
            return []

        # Assuming the first index item contains the combined string of keywords for simplicity
        raw_keywords = self._job_roles[role][0]
        required = [self._normalize_skill_local(s) for s in raw_keywords.split() if s.strip()]
        
        normalized_user_skills = [self._normalize_skill_local(skill) for skill in user_skills if skill.strip()]
        normalized_user_skills = list(dict.fromkeys(normalized_user_skills))

        missing = []
        for req in required:
            if not req:
                continue
            if req in normalized_user_skills:
                continue
            if get_close_matches(req, normalized_user_skills, n=1, cutoff=0.75):
                continue
            if req not in missing:
                missing.append(req)
            if len(missing) >= 5:
                break

        return missing

# Expose singleton globally
model_service = ModelService()
