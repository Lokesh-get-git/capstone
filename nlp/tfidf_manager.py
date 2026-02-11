from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from typing import List, Dict

class TfidfManager:
    def __init__(self):
        # We want words that appear in at least 1 document, but not *every* document
        # unique words = specific skills
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=100
        )
        self.is_fitted = False

    def fit_transform(self, claims: List[str]) -> pd.DataFrame:
        """
        Analyze a list of claims to find the most 'unique' words.
        """
        if not claims:
            return pd.DataFrame()

        tfidf_matrix = self.vectorizer.fit_transform(claims)
        self.is_fitted = True
        
        feature_names = self.vectorizer.get_feature_names_out()
        df = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names)
        return df

    def get_top_keywords(self, claims: List[str], top_n=5) -> List[str]:
        """
        Extract the most significant keywords from the resume.
        """
        df = self.fit_transform(claims)
        if df.empty:
            return []
            
        # Sum up scores for each word across all claims
        word_scores = df.sum().sort_values(ascending=False)
        return word_scores.head(top_n).index.tolist()