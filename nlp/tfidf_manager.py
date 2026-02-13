from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from typing import List, Tuple

class TfidfManager:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def calculate_similarity(self, resume_text: str, job_description: str) -> float:
        """Returns percentage similarity (0-100) between resume and job description."""
        if not job_description or not resume_text:
            return 0.0
            
        try:
            # Fit on both documents to build a shared vocabulary
            tfidf_matrix = self.vectorizer.fit_transform([resume_text, job_description])
            
            # Calculate Cosine Similarity
            # Row 0 is Resume, Row 1 is Job Description
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return round(similarity * 100, 2)
        except Exception:
            return 0.0

    def get_missing_keywords(self, resume_text: str, job_description: str, top_n: int = 5) -> List[str]:
        """
        Identify top keywords from the Job Description that are missing from the Resume.
        Uses Term Frequency (TF) on the JD since we only care about what's important *in that specific JD*.
        """
        if not job_description or not resume_text:
            return []

        try:
  
            vectorizer = TfidfVectorizer(stop_words='english', use_idf=False, max_features=50)
            jd_matrix = vectorizer.fit_transform([job_description])
            feature_names = vectorizer.get_feature_names_out()
            
            # 2. Get scores and sort
            df = pd.DataFrame(jd_matrix.toarray(), columns=feature_names)
            sorted_keywords = df.iloc[0].sort_values(ascending=False).head(20).index.tolist()


            resume_lower = resume_text.lower()
            
            missing = []
            for word in sorted_keywords:
        
                if word not in resume_lower:
                    missing.append(word)
                    
            return missing[:top_n]
            
        except Exception:
            return []