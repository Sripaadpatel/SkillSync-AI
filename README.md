🚀 SkillSync: AI-Powered Career Matchmaker

<div align="center">

Privacy-First • Local Inference • Hybrid Search • Gap Analysis

</div>

📖 Executive Summary

SkillSync is an intelligent microservice designed to bridge the gap between talent and opportunity. Unlike traditional Applicant Tracking Systems (ATS) that rely on rigid keyword matching, SkillSync uses Hybrid Semantic Search (Vector + Metadata) to understand the context of a candidate's profile.

Powered by Llama 3.2 and ChromaDB, it runs entirely locally, ensuring data privacy while providing enterprise-grade recommendations. It solves the "Cold Start" problem by intelligently extracting hard constraints (Location, Job Type) from resumes in a single pass.

✨ Key Features

Feature

Description

🚀 Hybrid Search Engine

Combines Vector Similarity (Semantic) with Metadata Filtering (Hard Constraints) for precise matching.

❄️ Cold Start Solver

Instantly extracts User ID, Location, and Role preferences from a PDF resume using a custom ETL pipeline.

🧠 Intelligent Parsing

Uses Llama 3.2 (Single-Pass Extraction) to understand resumes, not just regex them.

📊 AI Gap Analysis

Provides a detailed breakdown of Matching Skills, Missing Skills, and a Match Score (%) with actionable advice.

🔒 Privacy First

Zero data leakage. All inference runs on local hardware using Ollama and local Vector Stores.

🏗️ System Architecture

graph TD
    User([User / Client]) -->|Upload PDF| API[FastAPI Server]
    
    subgraph "SkillSync Core"
        API -->|Raw File| Parser[PDF Parser]
        Parser -->|Text| ETL[Llama 3.2 ETL Agent]
        ETL -->|Filters + Summary| Engine[Recommendation Engine]
        
        Engine -->|Query Vector| Chroma[(ChromaDB)]
        Engine -->|Apply Filters| Chroma
        
        Chroma -->|Top K Candidates| Engine
        
        Engine -->|Gap Analysis| Analyst[Llama 3.2 Reasoning Agent]
        Analyst -->|Structured JSON| API
    end
    
    API -->|Final Response| User


🛠️ Tech Stack

Backend: Python, FastAPI, Uvicorn

LLM Orchestration: LangChain

Local Inference: Ollama (Llama 3.2 3B Model)

Vector Database: ChromaDB

Embedding Model: nomic-embed-text

Data Processing: DuckDB, Pandas, PyPDF

🚀 Getting Started

Prerequisites

Python 3.10+ installed.

Ollama installed and running.

Pull the required models:

ollama pull llama3.2
ollama pull nomic-embed-text


Installation

Clone the repository

git clone [https://github.com/yourusername/skillsync.git](https://github.com/yourusername/skillsync.git)
cd skillsync


Install Dependencies

pip install -r requirements.txt


Initialize the Database

Note: You must run the indexer from the data directory.

cd data
python indexer.py
cd ..


Run the Server

python main.py


🔌 API Documentation

Once the server is running, access the interactive Swagger UI at:
👉 http://localhost:8000/docs

Primary Endpoint: Recommend Jobs

<details>
<summary>Click to view Request/Response details</summary>

POST /recommend

Request: multipart/form-data

file: PDF Resume (Binary)

Response (200 OK):

{
  "user_id": "candidate@example.com",
  "filters_applied": {
    "location": "New York, NY",
    "formatted_work_type": "Full-time"
  },
  "top_recommendation": {
    "title": "Senior Software Engineer",
    "company_name": "TechGlobal Inc.",
    "location": "New York, NY",
    "similarity_score": 0.89
  },
  "ai_analysis": {
    "match_score": "85%",
    "matching_skills": ["Python", "AWS", "FastAPI"],
    "missing_skills": ["Kubernetes", "GraphQL"],
    "advice": "Your backend experience is strong. To improve your match score, consider highlighting containerization projects."
  },
  "other_matches": [...]
}


</details>

📂 Project Structure

SkillSync/
├── data/
│   ├── data_processor.py    # Cleaning logic (DuckDB)
│   ├── indexer.py           # Vector embedding logic
│   ├── jobs_clean.csv       # Processed dataset
│   └── jobs_db/             # ChromaDB Persistent Store
├── main.py                  # FastAPI Application Entry Point
├── recsys_engine.py         # Core Business Logic & LLM Chains
├── pdf_parser.py            # PDF Extraction Utility
├── requirements.txt         # Dependencies
└── README.md                # Documentation


🤝 Contribution

Contributions are welcome! Please follow these steps:

Fork the repository.

Create a feature branch (git checkout -b feature/AmazingFeature).

Commit your changes (git commit -m 'Add some AmazingFeature').

Push to the branch (git push origin feature/AmazingFeature).

Open a Pull Request.

📄 License

Distributed under the MIT License. See LICENSE for more information.

<div align="center">
<sub>Built with ❤️ by SkillSync Team</sub>
</div>