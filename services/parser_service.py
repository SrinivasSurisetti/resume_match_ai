import re
import logging
from collections import Counter
import pdfplumber
import nltk
from config import SKILLS_FILE

# Initialize logging
logger = logging.getLogger(__name__)

# Ensure stopwords are available
try:
    nltk.download('stopwords', quiet=True)
except Exception as e:
    logger.warning(f"Could not download nltk stopwords: {e}")

class ResumeParser:
    _instance = None
    _skills_database = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResumeParser, cls).__new__(cls)
            cls._instance._skills_database = cls._instance._load_skill_database()
        return cls._instance

    def _load_skill_database(self):
        """Loads and caches the skills list from data/skills.txt."""
        try:
            with open(SKILLS_FILE, 'r', encoding='utf-8') as f:
                skills = [line.strip().lower() for line in f if line.strip() and not line.strip().startswith('#')]
            logger.info(f"Loaded {len(skills)} skills into memory from {SKILLS_FILE}.")
            return skills
        except Exception as e:
            logger.error(f"Failed to load skills file from {SKILLS_FILE}: {e}")
            # Fallback core skills if file goes missing
            return [
                'python','java','c++','machine learning','deep learning',
                'flask','django','react','angular','sql','html','css',
                'javascript','mongodb','mysql','pandas','numpy','tensorflow'
            ]

    def pdf_reader(self, file_path):
        """Safely extracts text from a PDF file returning an empty string if it fails."""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            if not text.strip():
                logger.warning(f"PDF {file_path} extracted empty text.")
            return text
        except Exception as e:
            logger.error(f"Failed to read PDF file {file_path}: {e}")
            return ""

    def clean_text_for_matching(self, text):
        """Normalizes string vectors removing special characters."""
        normalized = text.lower()
        normalized = re.sub(r'[^a-z0-9+#]+', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized

    def top_frequent_technical_words(self, text, top_n=5):
        """
        Fallback extraction measuring standard token frequency minus stopwords.
        
        [INTERVIEW EXPLANATION - Fallback NLP]
        If no exact skills are found in the dictionary, this acts as an NLP fallback.
        It tokenizes the resume, removes common English 'stopwords' (like 'and', 'the'),
        and returns the most mathematically frequent remaining keywords as suspected skills.
        """
        try:
            stop_words = set(nltk.corpus.stopwords.words('english'))
        except Exception:
            logger.warning("Stopwords corpus missing. Operating without stopwords filter.")
            stop_words = set()
            
        tokens = re.findall(r'\b[a-z0-9+#]{2,}\b', text)
        candidates = [tok for tok in tokens if tok not in stop_words and not tok.isdigit()]
        most_common = Counter(candidates).most_common(top_n)
        
        extracted = [word for word, _ in most_common]
        logger.info(f"Fallback matched {len(extracted)} potential frequent keyword tokens.")
        return extracted

    def extract_skills(self, text):
        """
        Extracts recognized skills from text based on dictionary matching.
        
        [INTERVIEW EXPLANATION - Token Matching Phase]
        This function iterates through our customized skills database. 
        It uses RegEx (Regular Expressions) to perform precise word-boundary matches \b
        on the resume string, guaranteeing 'C' doesn't falsely match against 'Macbook'.
        """
        normalized_text = self.clean_text_for_matching(text)
        unique_skills = []
        seen = set()

        for skill in self._skills_database:
            normalized_skill = self.clean_text_for_matching(skill)
            if not normalized_skill:
                continue
            
            pattern = r'(?<!\w)' + re.escape(normalized_skill) + r'(?!\w)'
            if re.search(pattern, normalized_text):
                if normalized_skill not in seen:
                    seen.add(normalized_skill)
                    unique_skills.append(normalized_skill)

        if not unique_skills:
            logger.warning("Exact skill sequence matching failed. Found 0 dictionary matches. Invoking fallback extractor.")
            return self.top_frequent_technical_words(normalized_text)
            
        logger.info(f"Successfully extracted {len(unique_skills)} hard-skill tokens from text.")
        return unique_skills

    def parse_resume(self, text):
        """Core endpoint combining component functions to output a finalized model dict."""
        email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        email_matches = email_pattern.findall(text)

        phone_pattern = re.compile(r'\+?\d[\d\s\-()]{8,}\d')
        phone_matches = phone_pattern.findall(text)

        skills = self.extract_skills(text)

        # Estimate pages based on lines per normal page structure
        estimated_pages = text.count('\n') // 50 + 1

        return {
            'name': 'User', # Often requires a NER library to extract accurately
            'email': email_matches[0] if email_matches else None,
            'mobile_number': phone_matches[0] if phone_matches else None,
            'skills': skills,
            'no_of_pages': estimated_pages
        }

# Expose a singleton instance correctly
parser_service = ResumeParser()
