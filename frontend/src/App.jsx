import { useState, useRef } from 'react';
import {
  Briefcase,
  User,
  FileText,
  Cpu,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Upload,
  Sparkles,
  CheckCircle2,
  HelpCircle,
  TrendingUp,
  AlertCircle,
  BookOpen,
  Check,
  Flame,
  Award,
  Terminal,
  Compass
} from 'lucide-react';
import './App.css';

// API Configuration
const API_URL = window.location.origin.includes("5173")
  ? "http://localhost:8000/api"
  : "/api";

const FALLBACK_SAMPLE_RESUME = `John Doe
Email: john.doe@email.com | Phone: (555) 123-4567 | LinkedIn: linkedin.com/in/johndoe

Summary
Experienced software engineer with 5+ years building scalable web applications. Passionate about clean code and system design.

Experience
Senior Software Engineer | TechCorp Inc. | 2021 - Present
- Led a team of 8 engineers to redesign the payment processing system, reducing transaction failures by 40%
- Architected microservices migration from monolith, improving deployment frequency by 3x
- Implemented CI/CD pipeline using Jenkins and Docker, cutting release time from 2 weeks to 2 days
- Mentored 4 junior developers through code reviews and pair programming sessions

Software Engineer | StartupXYZ | 2019 - 2021
- Developed RESTful APIs serving 50,000 daily active users using Python and FastAPI
- Optimized database queries resulting in 60% reduction in API response time
- Worked on various projects involving machine learning and data analysis
- Participated in agile ceremonies and helped with sprint planning

Education
Bachelor of Science in Computer Science | State University | 2019
- GPA: 3.7/4.0
- Relevant coursework: Algorithms, Data Structures, Machine Learning, Databases

Skills
Python, Java, JavaScript, React, Node.js, PostgreSQL, MongoDB, Docker, Kubernetes, AWS, Git, Jenkins, FastAPI, Flask, Redis, Kafka

Projects
Open Source Contribution - ML Pipeline Framework
- Built a Python framework for automating ML pipeline workflows with 500+ GitHub stars
- Implemented feature engineering module supporting 20+ transformation types

Personal Blog
- Write technical articles about system design and distributed systems

Certifications
- AWS Certified Solutions Architect - Associate (2022)
- Google Cloud Professional Data Engineer (2023)

Achievements
- Won first place in company-wide hackathon (2022)
- Speaker at PyCon Regional Conference on microservices patterns`;

function App() {
  // --- Form States ---
  const [targetRole, setTargetRole] = useState("Software Engineer");
  const [experienceYears, setExperienceYears] = useState(5);
  const [jobDescription, setJobDescription] = useState("");
  const [techStack, setTechStack] = useState("Python, Docker, AWS, Kubernetes");
  const [weaknesses, setWeaknesses] = useState("System Design, Public Speaking");
  const [file, setFile] = useState(null);

  // --- UI Layout States ---
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");
  const [dragActive, setDragActive] = useState(false);
  const [showTestNotice, setShowTestNotice] = useState(false);
  const fileInputRef = useRef(null);

  // --- Pipeline / Results States ---
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [errorMessage, setErrorMessage] = useState("");
  const [results, setResults] = useState(null);

  // --- Expandable Details States ---
  const [openQuestionIndex, setOpenQuestionIndex] = useState(null);
  const [showGradingDetails, setShowGradingDetails] = useState(false);
  const [openResources, setOpenResources] = useState({});

  // --- Step Metadata for Loading Animation ---
  const pipelineSteps = [
    { id: 1, text: "Extracting raw text from resume..." },
    { id: 2, text: "Initializing Resume Analyst Agent (Parsing & ML Risk Detection)..." },
    { id: 3, text: "Running Question Strategist Agent (Devising Interview Plan)..." },
    { id: 4, text: "Invoking Difficulty Planner Agent (Structuring warmup -> challenge flow)..." },
    { id: 5, text: "Activating Question Generator Agent (Synthesizing context-aware prompts)..." },
    { id: 6, text: "Engaging Validator Agent (Conducting strict quality checks & refinement loop)..." },
    { id: 7, text: "Finalizing Coach Agent (Researching external study resources)..." }
  ];

  // --- Drag and Drop Handlers ---
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  const handleUploadSample = async () => {
    try {
      let text = FALLBACK_SAMPLE_RESUME;
      let filename = "sample_resume.txt";
      
      try {
        const response = await fetch(`${API_URL}/sample-resume`);
        if (response.ok) {
          const data = await response.json();
          if (data.text) {
            text = data.text;
            filename = data.filename || "sample_resume.txt";
          }
        }
      } catch (err) {
        console.warn("Could not fetch sample resume from backend, using embedded fallback:", err);
      }
      
      const sampleFile = new File([text], filename, { type: "text/plain" });
      setFile(sampleFile);
      
      // Ensure targetRole and experienceYears are set correctly for the sample
      setTargetRole("Software Engineer");
      setExperienceYears(5);
      
      // Say that this button is for testing only, and note the Groq free tier limit
      setShowTestNotice(true);
    } catch (err) {
      console.error(err);
      setErrorMessage("Failed to prepare sample resume: " + err.message);
    }
  };

  // --- Analyze Resume Trigger ---
  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!file) return;

    setIsAnalyzing(true);
    setErrorMessage("");
    setResults(null);
    setLoadingStep(0);

    try {
      // 1. File Upload & Text Extraction
      setLoadingStep(1);
      const formData = new FormData();
      formData.append("file", file);

      const extractResponse = await fetch(`${API_URL}/extract_text`, {
        method: "POST",
        body: formData,
      });

      if (!extractResponse.ok) {
        const errorData = await extractResponse.json();
        throw new Error(errorData.detail || "Failed to extract text from resume.");
      }

      const extractData = await extractResponse.json();
      const resumeText = extractData.text;

      // 2. Run multi-agent pipeline
      setLoadingStep(2);

      // Simulate sequential step activation to keep candidate engaged
      const stepInterval = setInterval(() => {
        setLoadingStep(prev => {
          if (prev < 6) return prev + 1;
          clearInterval(stepInterval);
          return prev;
        });
      }, 2500);

      const payload = {
        resume_text: resumeText,
        job_description: jobDescription,
        candidate_profile: {
          target_role: targetRole,
          experience_years: parseInt(experienceYears) || 0,
          tech_stack: techStack.split(",").map(t => t.trim()).filter(Boolean),
          self_declared_weaknesses: weaknesses.split(",").map(w => w.trim()).filter(Boolean)
        }
      };

      const analyzeResponse = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      clearInterval(stepInterval);

      if (!analyzeResponse.ok) {
        const errorData = await analyzeResponse.json();
        throw new Error(errorData.detail || "Analysis pipeline failed.");
      }

      const data = await analyzeResponse.json();
      setLoadingStep(7);

      // Short delay to let the user see step 7 complete
      setTimeout(() => {
        setResults(data);
        setIsAnalyzing(false);
        setActiveTab("overview");
      }, 800);

    } catch (err) {
      console.error(err);
      setErrorMessage(err.message || "An unexpected error occurred during analysis.");
      setIsAnalyzing(false);
    }
  };

  // Toggle Insight Resources list
  const toggleResource = (index) => {
    setOpenResources(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  // Helper: map feature names from ML grading
  const getFeatureDisplayName = (feature) => {
    switch (feature) {
      case "sem_num_keywords": return "Technical Depth";
      case "clarity_has_metrics": return "Use of Metrics";
      case "quant_has_weak_language": return "Weak Language";
      case "txt_word_count": return "Detail Level";
      default: return feature.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
    }
  };

  return (
    <div className="app-container">
      {/* ==========================================
         SIDEBAR: Inputs and Controls
         ========================================== */}
      <aside className="sidebar">
        <div className="brand-section">
          <span className="brand-icon">🐛</span>
          <h1 className="brand-title">Ai Interview Preparation System</h1>
        </div>

        <h3 className="sidebar-section-title">Candidate Profile</h3>

        <form onSubmit={handleAnalyze} style={{ border: 'none', padding: 0, marginTop: 0, display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

          {/* File Drag and Drop */}
          <div className="form-group">
            <label className="form-label">📂 Upload Resume</label>
            <div
              className={`file-upload-container ${dragActive ? 'drag-active' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={triggerFileInput}
            >
              <input
                type="file"
                ref={fileInputRef}
                style={{ display: 'none' }}
                accept=".pdf,.txt"
                onChange={handleFileChange}
                disabled={isAnalyzing}
              />
              <Upload className="file-upload-icon" size={24} />
              <p className="file-upload-text">Drag & Drop Resume here</p>
              <span className="file-upload-subtext">Supports PDF or TXT</span>
            </div>

            <button
              type="button"
              className="btn-testing"
              onClick={handleUploadSample}
              disabled={isAnalyzing}
            >
              📄 Load Sample Resume
            </button>
            <span className="testing-note">
              ⚠️ For testing only. Uses Groq free tier—please use mindfully.
            </span>

            {file && (
              <div className="file-selected-badge" style={{ marginTop: '0.4rem' }}>
                <FileText size={14} />
                <span>{file.name}</span>
              </div>
            )}
          </div>

          <div className="form-group">
            <label className="form-label">⏳ Years of Experience</label>
            <input
              type="number"
              className="form-input"
              value={experienceYears}
              onChange={(e) => setExperienceYears(e.target.value)}
              min="0"
              max="50"
              required
              disabled={isAnalyzing}
            />
          </div>

          <div className="form-group">
            <label className="form-label">💻 Tech Stack</label>
            <textarea
              className="form-textarea"
              value={techStack}
              onChange={(e) => setTechStack(e.target.value)}
              placeholder="Python, Docker, Kubernetes..."
              disabled={isAnalyzing}
              rows={2}
            />
          </div>

          <div className="form-group">
            <label className="form-label">⚠️ Known Weaknesses</label>
            <textarea
              className="form-textarea"
              value={weaknesses}
              onChange={(e) => setWeaknesses(e.target.value)}
              placeholder="System Design, Public Speaking..."
              disabled={isAnalyzing}
              rows={2}
            />
          </div>

          <hr style={{ borderColor: 'var(--border-color)', margin: '0.25rem 0' }} />

          {/* --- SECTION 2: TARGET JOB DETAILS --- */}
          <h3 className="sidebar-section-title">Target Job Details</h3>

          <div className="form-group">
            <label className="form-label">🎯 Target Role</label>
            <input
              type="text"
              className="form-input"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              placeholder="e.g. Software Engineer"
              required
              disabled={isAnalyzing}
            />
          </div>

          <div className="form-group">
            <label className="form-label">📝 Job Description (Optional)</label>
            <textarea
              className="form-textarea"
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste job description to calculate Relevance Score..."
              disabled={isAnalyzing}
              rows={3}
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            disabled={!file || isAnalyzing}
          >
            <Sparkles size={16} />
            <span>🚀 Analyze Resume</span>
          </button>
        </form>
      </aside>

      {/* ==========================================
         MAIN CONTENT: Dashboards and Results
         ========================================== */}
      <main className="main-content">

        {/* --- STATE 1: ERROR DISPLAY --- */}
        {errorMessage && (
          <div className="error-card">
            <AlertTriangle className="error-icon" size={48} />
            <h3 className="error-title">Analysis Failed</h3>
            <p className="error-message">{errorMessage}</p>
            <button
              className="btn-primary"
              onClick={() => setErrorMessage("")}
              style={{ marginTop: '0.5rem', padding: '0.5rem 1rem', fontSize: '0.85rem' }}
            >
              Dismiss
            </button>
          </div>
        )}

        {/* --- STATE 2: PIPELINE RUNNING LOADING DISPLAY --- */}
        {isAnalyzing && (
          <div className="loading-container">
            <div className="pulsing-loader">
              <div className="loader-circle"></div>
              <span className="loader-inner">🧠</span>
            </div>
            <h3 className="loading-heading">Running Multi-Agent Simulation...</h3>

            <div className="steps-tracker">
              {pipelineSteps.map((step) => {
                const isCompleted = loadingStep > step.id;
                const isActive = loadingStep === step.id;
                return (
                  <div
                    key={step.id}
                    className={`step-row ${isCompleted ? 'completed' : ''} ${isActive ? 'active' : ''}`}
                  >
                    <div className="step-indicator-dot">
                      {isCompleted ? "✓" : step.id}
                    </div>
                    <span className="step-text-main">{step.text}</span>
                    <div className="step-spinner-micro">⚙️</div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* --- STATE 3: WELCOME EMPTY STATE DISPLAY --- */}
        {!isAnalyzing && !results && !errorMessage && (
          <div className="empty-state">
            <div className="welcome-icon-box">🤖</div>
            <h2 className="welcome-title">AI Interview Preparation System</h2>
            <p className="welcome-desc">
              Prepare yourself for high-level technical interviews. Our intelligent, multi-agent AI framework (powered by LangGraph and Groq) maps out resume claim risks, determines role readiness, plans strategic question flows, and delivers tailored expert coaching.
            </p>

            <div className="pipeline-section">
              <h4 className="pipeline-title">Cyclical State Orchestration Pipeline</h4>
              <div className="pipeline-flow">
                <div className="pipeline-node">
                  <User size={14} />
                  <span>Resume Analyst</span>
                </div>
                <span className="pipeline-arrow">➔</span>
                <div className="pipeline-node">
                  <Compass size={14} />
                  <span>Question Strategist</span>
                </div>
                <span className="pipeline-arrow">➔</span>
                <div className="pipeline-node">
                  <Briefcase size={14} />
                  <span>Difficulty Planner</span>
                </div>
                <span className="pipeline-arrow">➔</span>
                <div className="pipeline-node">
                  <Terminal size={14} />
                  <span>Question Generator</span>
                </div>
                <span className="pipeline-arrow">➔</span>
                <div className="pipeline-node">
                  <Award size={14} />
                  <span>Validator Agent</span>
                </div>
                <span className="pipeline-arrow">➔</span>
                <div className="pipeline-node">
                  <Cpu size={14} />
                  <span>Coach Agent</span>
                </div>
              </div>
            </div>

            <div style={{ marginTop: '1.5rem', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1.25rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              💡 <strong>Get Started:</strong> Fill out your target role, years of experience, upload your resume in the left panel, and click <strong>🚀 Analyze Resume</strong> to launch the simulation.
            </div>
          </div>
        )}

        {/* --- STATE 4: ANALYSIS RESULTS DASHBOARD --- */}
        {!isAnalyzing && results && (
          <div className="tabs-wrapper">

            {/* Header Metrics */}
            <div className="dashboard-header">
              <div>
                <h2 className="dashboard-title">Dashboard: {targetRole}</h2>
                <p className="dashboard-subtitle">Multi-Agent assessment of claims, gaps, and weaknesses</p>
              </div>
            </div>

            {/* Dashboard 4-Column Cards */}
            <div className="metrics-grid">

              {/* Card 1: Readiness Score */}
              <div className="metric-card">
                <div className="metric-header">
                  <span className="metric-title">Readiness Score</span>
                  <div className="metric-icon-wrapper" style={{ color: 'var(--accent-secondary)' }}>
                    <TrendingUp size={16} />
                  </div>
                </div>
                <div className="metric-value-container">
                  <span className="metric-value">{results.readiness_analysis?.score || 0}/100</span>
                  {results.readiness_analysis?.level && (
                    <span className="metric-delta positive">
                      {results.readiness_analysis.level}
                    </span>
                  )}
                </div>
                <span
                  className="metric-tooltip-trigger"
                  title="Derived from the Resume Analyst agent. Evaluated based on quantifiable metrics, verifiability, and section completeness."
                >
                  <HelpCircle size={12} style={{ marginRight: '4px' }} />
                  What is this?
                </span>
              </div>

              {/* Card 2: Claims Analyzed */}
              <div className="metric-card">
                <div className="metric-header">
                  <span className="metric-title">Claims Analyzed</span>
                  <div className="metric-icon-wrapper" style={{ color: '#c084fc' }}>
                    <FileText size={16} />
                  </div>
                </div>
                <div className="metric-value-container">
                  <span className="metric-value">{results.claims?.length || 0}</span>
                  <span className="metric-delta neutral">Claims</span>
                </div>
                <span
                  className="metric-tooltip-trigger"
                  title="Total distinct achievements and professional statements extracted from your resume."
                >
                  <HelpCircle size={12} style={{ marginRight: '4px' }} />
                  What is this?
                </span>
              </div>

              {/* Card 3: Skill Gaps */}
              <div className="metric-card">
                <div className="metric-header">
                  <span className="metric-title">Skill Gaps</span>
                  <div className="metric-icon-wrapper" style={{ color: 'var(--risk-medium)' }}>
                    <AlertCircle size={16} />
                  </div>
                </div>
                <div className="metric-value-container">
                  <span className="metric-value">{results.skill_gaps?.missing_skills?.length || 0}</span>
                  {results.skill_gaps?.missing_skills?.length > 0 && (
                    <span className="metric-delta negative">
                      -{results.skill_gaps.missing_skills.length} Gaps
                    </span>
                  )}
                </div>
                <span
                  className="metric-tooltip-trigger"
                  title="Critical skills required for your target role that were not found in your resume."
                >
                  <HelpCircle size={12} style={{ marginRight: '4px' }} />
                  What is this?
                </span>
              </div>

              {/* Card 4: Vulnerabilities */}
              <div className="metric-card">
                <div className="metric-header">
                  <span className="metric-title">Vulnerabilities</span>
                  <div className="metric-icon-wrapper" style={{ color: 'var(--risk-high)' }}>
                    <AlertTriangle size={16} />
                  </div>
                </div>
                <div className="metric-value-container">
                  <span className="metric-value">{results.vulnerability_map?.top_weaknesses?.length || 0}</span>
                  <span className="metric-delta negative">Critical</span>
                </div>
                <span
                  className="metric-tooltip-trigger"
                  title="Weaknesses flagged by the Vulnerability Mapper, such as vague statistics or missing metrics in key achievements."
                >
                  <HelpCircle size={12} style={{ marginRight: '4px' }} />
                  What is this?
                </span>
              </div>

            </div>

            {/* Premium Tab Navigation */}
            <div className="tabs-header">
              <button
                className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}
              >
                📊 Resume Analysis
              </button>
              <button
                className={`tab-btn ${activeTab === 'practice' ? 'active' : ''}`}
                onClick={() => setActiveTab('practice')}
              >
                🎤 Practice Interview
              </button>
              <button
                className={`tab-btn ${activeTab === 'coach' ? 'active' : ''}`}
                onClick={() => setActiveTab('coach')}
              >
                💡 AI Coach
              </button>
            </div>

            {/* ==========================================
               TAB 1 PANEL: RESUME ANALYSIS
               ========================================== */}
            {activeTab === 'overview' && (
              <div className="tab-panel grid-2col">
                {/* Left Column */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

                  {/* Claim Risk Assessment */}
                  <div className="panel-card">
                    <div className="panel-header">
                      <h4 className="panel-title">🔍 Claim Risk Assessment</h4>
                      <p className="panel-caption">Analyzed by the Resume Analyst Agent. Evaluates claim specificity, credibility, and weak words using a calibrated ML model.</p>
                    </div>

                    {results.claims && results.claims.length > 0 ? (
                      <div className="table-wrapper">
                        <table className="claims-table">
                          <thead>
                            <tr>
                              <th>Claim Text</th>
                              <th style={{ width: '120px' }}>Risk Level</th>
                            </tr>
                          </thead>
                          <tbody>
                            {results.claims.map((claim, idx) => (
                              <tr key={idx}>
                                <td>{claim.text}</td>
                                <td>
                                  <span className={`risk-badge ${(claim.risk_label || 'low').toLowerCase()}`}>
                                    {claim.risk_label || 'Low'}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                        No claims extracted.
                      </div>
                    )}
                  </div>

                  {/* Job Fit Analysis */}
                  {jobDescription ? (
                    <div className="panel-card">
                      <div className="panel-header">
                        <h4 className="panel-title">🎯 Job Fit Analysis</h4>
                        <p className="panel-caption">Evaluated by comparing your overall profile match against the provided Job Description details.</p>
                      </div>

                      <div className="job-fit-container">
                        <div>
                          <div className="progress-header">
                            <span className="progress-title">Overall Match Score</span>
                            <span className="progress-value">{results.readiness_analysis?.relevance_score || 0}%</span>
                          </div>
                          <div className="progress-bar-bg" style={{ marginTop: '0.4rem' }}>
                            <div
                              className="progress-bar-fill"
                              style={{ width: `${results.readiness_analysis?.relevance_score || 0}%` }}
                            ></div>
                          </div>
                        </div>

                        {results.readiness_analysis?.missing_keywords && results.readiness_analysis.missing_keywords.length > 0 && (
                          <div className="keywords-section">
                            <span className="keywords-label">⚠️ Missing Keywords</span>
                            <div className="keyword-pills">
                              {results.readiness_analysis.missing_keywords.map((kw, i) => (
                                <span key={i} className="keyword-pill">{kw}</span>
                              ))}
                            </div>
                            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                              Adding these terms and showcasing relevant experience on your resume will optimize your applicant scoring.
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="panel-card" style={{ background: 'rgba(255,255,255,0.02)', borderStyle: 'dashed' }}>
                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem', textAlign: 'center', padding: '1rem' }}>
                        <Sparkles size={20} style={{ color: 'var(--accent-secondary)' }} />
                        <h5 style={{ fontWeight: 600, color: 'var(--text-heading)' }}>Unlock Job Fit & Keyword Gaps</h5>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', maxWidth: '400px' }}>
                          Provide a Job Description in the Advanced Settings in the sidebar to calculate match scores and detect missing keywords.
                        </p>
                      </div>
                    </div>
                  )}

                </div>

                {/* Right Column */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

                  {/* Vulnerabilities Panel */}
                  <div className="panel-card">
                    <div className="panel-header">
                      <h4 className="panel-title">⚠️ Key Vulnerabilities</h4>
                      <p className="panel-caption">Common pitfalls identified by the Vulnerability Mapper Agent.</p>
                    </div>

                    <div className="vulnerabilities-list">
                      {results.vulnerability_map?.top_weaknesses && results.vulnerability_map.top_weaknesses.length > 0 ? (
                        results.vulnerability_map.top_weaknesses.map((weakness, i) => (
                          <div key={i} className="vuln-badge-item">
                            <AlertTriangle size={14} className="vuln-icon" />
                            <span>{weakness}</span>
                          </div>
                        ))
                      ) : (
                        <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                          No high risk vulnerabilities identified!
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Interviewer Focus Panel */}
                  <div className="panel-card">
                    <div className="panel-header">
                      <h4 className="panel-title">🎯 Interviewer Focus Areas</h4>
                      <p className="panel-caption">Predicted technical topics and focus vectors based on your profile.</p>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                      {results.vulnerability_map?.interview_focus && results.vulnerability_map.interview_focus.length > 0 ? (
                        results.vulnerability_map.interview_focus.map((focus, i) => (
                          <div key={i} className="focus-item">
                            <CheckCircle2 size={12} className="focus-bullet" />
                            <span>{focus}</span>
                          </div>
                        ))
                      ) : (
                        <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                          Focus areas not generated.
                        </div>
                      )}
                    </div>
                  </div>

                </div>
              </div>
            )}

            {/* ==========================================
               TAB 2 PANEL: PRACTICE INTERVIEW QUESTIONS
               ========================================== */}
            {activeTab === 'practice' && (
              <div className="tab-panel panel-card">
                <div className="panel-header">
                  <h4 className="panel-title">📚 Tailored Interview Questions</h4>
                  <p className="panel-caption">Generated based on your resume's weaknesses by the Generator Agent, and verified for consistency and depth by the Validator Agent.</p>
                </div>

                <div className="questions-list">
                  {results.questions && results.questions.length > 0 ? (
                    results.questions.map((q, idx) => {
                      const isOpen = openQuestionIndex === idx;
                      return (
                        <div key={idx} className={`question-item ${isOpen ? 'open' : ''}`}>

                          {/* Accordion Trigger */}
                          <div
                            className="question-header"
                            onClick={() => setOpenQuestionIndex(isOpen ? null : idx)}
                          >
                            <div className="question-title-group">
                              <span className="question-number">Q{idx + 1}</span>
                              <span className="question-text">{q.question}</span>
                            </div>
                            <div className="question-meta-group">
                              {q.difficulty && (
                                <span className={`difficulty-badge ${(q.difficulty || 'core').toLowerCase()}`}>
                                  {q.difficulty}
                                </span>
                              )}
                              <ChevronDown className="question-toggle-icon" size={16} />
                            </div>
                          </div>

                          {/* Accordion Content */}
                          {isOpen && (
                            <div className="question-body">
                              {q.target_claim && (
                                <div className="target-claim-section">
                                  <div className="target-claim-label">Target Resume Claim</div>
                                  <div className="target-claim-text">"{q.target_claim}"</div>
                                </div>
                              )}

                              <div className="question-details-grid">
                                <div className="details-column">
                                  <span className="details-column-title">Interviewer Reasoning</span>
                                  <p className="reasoning-text">{q.reasoning || "Analyzes depth of experience regarding this specific claim."}</p>
                                </div>
                                <div className="details-column">
                                  <span className="details-column-title">Recommended Answer Structure</span>
                                  <div className="points-list">
                                    {q.expected_answer_points && q.expected_answer_points.length > 0 ? (
                                      q.expected_answer_points.map((pt, pIdx) => (
                                        <div key={pIdx} className="point-item">
                                          <Check size={12} className="point-check" />
                                          <span>{pt}</span>
                                        </div>
                                      ))
                                    ) : (
                                      <div style={{ fontStyle: 'italic', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                        No recommendations provided.
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>
                          )}

                        </div>
                      );
                    })
                  ) : (
                    <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                      No tailored practice questions generated.
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* ==========================================
               TAB 3 PANEL: PERSONALIZED COACHING
               ========================================== */}
            {activeTab === 'coach' && (
              <div className="tab-panel coach-insights-section">

                {/* How the AI Graded Your Resume */}
                {results.risk_analysis?.model_insights && results.risk_analysis.model_insights.length > 0 && (
                  <div className="panel-card ai-grading-card">
                    <div
                      className="grading-accordion-trigger"
                      onClick={() => setShowGradingDetails(!showGradingDetails)}
                    >
                      <h4 className="grading-accordion-title">
                        <Cpu size={16} style={{ color: 'var(--accent-secondary)' }} />
                        <span>🤖 How the AI Graded Your Resume</span>
                      </h4>
                      <span>{showGradingDetails ? "▲" : "▼"}</span>
                    </div>

                    {showGradingDetails && (
                      <div className="grading-accordion-content">
                        <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '1rem', lineHeight: '1.45' }}>
                          These are the key quantitative features and neural signals that the Machine Learning model processed to calculate risk probabilities on your resume claims:
                        </p>

                        <div className="feature-weights-grid">
                          {results.risk_analysis.model_insights.map(([feature, weight], idx) => {
                            const isPositive = weight > 0;
                            return (
                              <div key={idx} className="feature-card">
                                <span className="feature-name">{getFeatureDisplayName(feature)}</span>
                                <div className="feature-weight-container">
                                  <span className="feature-weight">{weight.toFixed(2)}</span>
                                  <span className={`feature-signal ${isPositive ? 'positive' : 'negative'}`}>
                                    {isPositive ? "✓ Positive" : "⚠️ Weak Signal"}
                                  </span>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Coaching Insights Flex Cards */}
                {results.coaching_insights && results.coaching_insights.length > 0 ? (
                  <div className="panel-card">
                    <div className="panel-header">
                      <h4 className="panel-title">👨‍🏫 AI Interview Coach Insights</h4>
                      <p className="panel-caption">Synthesized coaching insights based on resume pitfalls, structured by priority and study domain.</p>
                    </div>

                    <div className="coach-insights-section">
                      {/* Group Insights by Category */}
                      {["Strength", "Weakness", "Practice Tip", "Study Area"].map((cat) => {
                        const catInsights = results.coaching_insights.filter(i => i.category === cat);
                        if (catInsights.length === 0) return null;

                        return (
                          <div key={cat} className="category-group">
                            <h5 className="category-title">{cat}s</h5>
                            <div className="insights-flex-grid">
                              {catInsights.map((insight, idx) => {
                                const priority = insight.priority || "Medium";
                                const priorityClass = priority.toLowerCase();
                                const globalIdx = `${cat}-${idx}`;
                                const isResourcesOpen = !!openResources[globalIdx];

                                return (
                                  <div key={idx} className="insight-card">
                                    <div className="insight-header">
                                      <span className={`priority-bullet ${priorityClass}`} />
                                      <span className="insight-topic">{insight.topic}</span>
                                    </div>
                                    <p className="insight-advice">{insight.advice}</p>

                                    {insight.resources && insight.resources.length > 0 && (
                                      <div className="resources-drawer">
                                        <button
                                          className="resources-toggle-btn"
                                          onClick={() => toggleResource(globalIdx)}
                                        >
                                          <BookOpen size={10} />
                                          <span>{isResourcesOpen ? "Hide Study Resources" : "View Study Resources"}</span>
                                        </button>

                                        {isResourcesOpen && (
                                          <ul className="resources-list">
                                            {insight.resources.map((res, rIdx) => (
                                              <li key={rIdx} className="resource-item">
                                                <Check size={8} className="resource-bullet" style={{ marginTop: '0.2rem' }} />
                                                <span>{res}</span>
                                              </li>
                                            ))}
                                          </ul>
                                        )}
                                      </div>
                                    )}
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ) : (
                  <div className="panel-card" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                    No coaching insights generated.
                  </div>
                )}

              </div>
            )}

          </div>
        )}

      </main>

      {showTestNotice && (
        <div className="modal-backdrop" onClick={() => setShowTestNotice(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header-icon">⚠️</div>
            <h3 className="modal-title">Testing Only</h3>
            <div className="modal-body">
              <p>This button is for testing purposes only.</p>
              <div className="modal-highlight-box" style={{ marginTop: '1rem' }}>
                <strong>Important Notice:</strong>
                <span>We are using the Groq free tier, so please use the site mindfully.</span>
              </div>
            </div>
            <div className="modal-actions">
              <button type="button" className="btn-primary" style={{ minWidth: '120px' }} onClick={() => setShowTestNotice(false)}>
                Got it
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
