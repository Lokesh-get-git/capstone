#risk_classifier
# In tempmain.py (or a training script):
from risk_classifier import RiskClassifier
# # Train + Save
# clf = RiskClassifier()
# clf.train("synthetic_resume_training.csv")
# clf.save("models/risk_model.joblib")  # creates models/ dir automatically

# Later, load without retraining:
clf2 = RiskClassifier.load("models/risk_model.joblib")
result = clf2.predict({"txt_char_count":39,"txt_word_count":5,"txt_avg_word_length":7.0,"txt_sentence_count":1,"txt_words_per_sentence":5.0,"txt_uppercase_ratio":0.1026,"txt_punctuation_count":0,"txt_starts_with_verb":0,"txt_ends_with_period":0,"txt_has_parentheses":0,"quant_number_count":0,"quant_has_percentage":0,"quant_has_dollar":0,"quant_has_multiplier":0,"quant_verb_count":0,"quant_first_word_is_verb":0,"quant_has_weak_language":1,"quant_metric_density":0.0,"struct_has_bullet":0,"struct_comma_count":0,"struct_has_list_structure":0,"struct_and_count":0,"struct_clause_count":1,"struct_has_comparison":0,"struct_is_experience":0,"struct_is_project":1,"struct_is_summary":0,"struct_is_education":0,"struct_is_skills":0,"sem_num_keywords":0,"sem_has_language":0,"sem_has_framework":0,"sem_has_database":0,"sem_has_cloud":0,"sem_has_concept":0,"sem_tech_breadth":0,"sem_token_count":6,"clarity_score":0.12,"clarity_has_action_verb":0,"clarity_has_metrics":0,"clarity_word_count":5,"text":"Responsible for API gateway maintenance"})  # instant, no training
print(result)