1. ML models:

job readiness scorer and risk classifier could be improved. 

-currently risk classifier "rarely classifies high or very high claims."
-readiness scorer "always stays between 30-80" no matter the resume.
 
  ->solutions:
    better dataset and better models.
    -current "synthetic data barely represents real resumes" but given the time constraint this is the best i can afford
    -even though "i used meta data" instead of actual words it still "lacks real pattern" that can be seen in real resumes.
    -custom pytorch model might give me "more control" on its training giving better or worse results. "still heavily depends on dataset"

2. resume parser:

resume parser is not perfect using "regular expressions for extraction."

-rule based extraction can never beat smart claim extrations using ai.
    
    ->solution: "should've used llm in resume analyst" to get best results but for some reason i thought its not the intent of the task and this will impress more(bad decision). i thought this also "reduces llm use, decreasing cost."

3. job fit analysis:

this is just an optional feature where im using tfidf cosine similarity, rarely accurate as im just finding similarity between resume and jd.

4. Questions:

-A total of 4 agents contributed to questions as a result sometimes they gets conflicts between them. mostly validator and generator. They all get context variables(for personalised questions) specific to them in prompts. so something an agent know may or may not be known by other agent which is good(Seperation of concerns) but this also means its hard for them to coordinate as they dont know others intent to fullest.

-validator and generator loop eating a lot of tokens as they loop multiple times. i limited validator max iterations to 3 but still thats a lot of cost. Fix: could make "validator validate and change failed questions itself" but i dont know the intention of the task.

## Final note(major improvements):

1. readiness scorer, risk classifier (our flagship feature)
2. Better questions (another flagship feature of the task)

They are temporarily calibrated to be stable for presentation. but to get best real life accuracy and more relaible results. definetly need more training and tuning