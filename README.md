# 🧠 Intelligent Interview Prep System (Capstone)

A sophisticated, multi-agent AI system designed to prepare candidates for high-level technical interviews. This project leverages **LangGraph** to orchestrate a team of specialized AI agents, combining **Rule-Based Parsing**, **Machine Learning**, and **Generative AI** to deliver a bespoke interview experience.

# Read improvements.md to know what could be and needs to be improved
---

## 🏗️ Technical Architecture

The system follows a **cyclical, state-dependent workflow**. Data flows through a shared [AgentState] object, modified by each node in the graph.

### 1. State Management ([agents/state.py])
*   **[AgentState]**: The backbone of the application.
    *   **Inputs**: [resume_text], `job_description`, `candidate_profile`.
    *   **Analysis Data**: [claims] (List[ResumeClaim]), `risk_analysis`, `readiness_analysis`.
    *   **Flow Control**: `retry_count` (int), `validation_results` (List).
    *   **Metrics**: [total_cost] (Annotated[float, operator.add] - Reducer).
    *   **Outputs**: `generated_questions`, `coaching_insights`.

### 2. Core Agents & Logic

#### 🕵️ Resume Analyst ([agents/resume_analyst.py])
*   **Function**: Transforms raw text into structured data.
*   **Intricacy**:
    *   **Hybrid Parsing**: Uses `pdfplumber` for layout preservation but falls back to regex for specific section extraction ([parsers/resume_parser.py].)
    *   **ML Risk Detection**: Calls [ml/risk_classifier.py] (Logistic Regression) to predict if a claim is "High Risk" (vague/unsubstantiated).
    *   **Output**: Populates [claims]`risk_analysis`, and `vulnerability_map` in state.

#### 🧠 Question Strategist ([agents/question_strategist.py])
*   **Function**: The strategic brain.
*   **Intricacy**:
    *   Analyzes [vulnerabilities] and `skill_gaps` to form a high-level *Interview Strategy* (e.g., "Aggressively probe System Design due to lack of concrete examples").
    *   **LLM Choice**: Uses `llama-3.3-70b-versatile` for high-reasoning capability.

#### 📅 Difficulty Planner ([agents/difficulty_planner.py])
*   **Function**: Context-aware scheduler.
*   **Intricacy**:
    *   Maps the *Strategy* into a concrete 15-question plan.
    *   **Algorithm**: Enforces a "Warmup -> Core -> Challenge" progression based on the candidate's `readiness_score`.

#### ✍️ Question Generator ([agents/question_generator.py])
*   **Function**: The implementation engine.
*   **Intricacy**:
    *   **Dual Mode**: 
        1.  **Standard**: Generates questions from the Plan.
        2.  **Refinement**: If Validation fails, it enters a *Refinement Loop*, taking `feedback_context` to rewrite specific questions.
    *   **Cost Awareness**: Tracks token usage for every call (`CostTracker.track_cost`).

#### ⚖️ Validator ([agents/validator.py])
*   **Function**: Quality Control.
*   **Intricacy**:
    *   **Strict Rules**: Checks for "Single Thought", "Conversational Tone", and "No Compound Questions".
    *   **Routing**: If failures > 0, signals [orchestrator.py] to route back to [question_generator] (up to 3 times).

#### 🎓 Coach ([agents/coach.py])
*   **Function**: Post-interview analysis.
*   **Intricacy**:
    *   Synthesizes the entire session (Risks + Questions) into actionable advice.
    *   **Search Integration** (Optional): Can use `TavilySearchResults` to find learning resources for identified gaps.

### 3. Orchestration 
*   **Graph Definition**: Defines the `StateGraph` nodes and edges.
*   **Conditional Edge**: [route_after_validator] logic determines if the flow loops back or proceeds to coaching.
*   **Entry Point**: [run_interview_pipeline] initializes the state and compiles the graph.

---

## 🧠 Machine Learning Components

### Risk Classifier ([ml/risk_classifier.py])
*   **Model**: Logistic Regression (Calibrated).
*   **Features**: Text length, specificity (regex), weak words count.
*   **Training**: Trained on synthetic resume data ([synthetic_resume_training.csv]).
*   **Usage**: Real-time prediction during the Analyst phase.

### Readiness Scorer ([ml/readiness_scorer.py])
*   **Logic**: Hybrid Scoring.
    *   **Base**: Keyword matching against Job Description.
    *   **Penalty**: Subtracts points for "High Risk" claims.
    *   **Result**: 0-100 Score + Level (Beginner/Intermediate/Expert).

---



## 🛠️ API & UI

*   **FastAPI ([api/main.py])**: Exposes the [run_interview_pipeline](file:///d:/work/training/capstone/agents/orchestrator.py#81-138) as a REST endpoint (`/analyze`).
*   **Streamlit ([ui/app.py])**: Provides an interactive dashboard for users to upload resumes and view results.

### How to Run
See **[SETUP_GUIDE.md](SETUP_GUIDE.md)** for installation and execution instructions.
