import os
import json
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from pdf_parser import ResumeParser


CHROMA_PATH = os.path.join("data", "jobs_db")
EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3.1"

class SkillSyncEngine:
    def __init__(self):
        print("Initializing SkillSyncEngine...")
        self.embedder = OllamaEmbeddings(model=EMBED_MODEL)
        self.llm = ChatOllama(model=LLM_MODEL, temperature=0, format="json")
        self.llm2 = ChatOllama(model=LLM_MODEL, temperature=0.3)
        # Connect the existing ChromaDB
        if os.path.exists(CHROMA_PATH):
            self.vector_store = Chroma(
                embedding_function=self.embedder,
                persist_directory=CHROMA_PATH,
                collection_name="jobs_postings"
            )
            print(f"Connected to ChromaDB at '{CHROMA_PATH}'.")
        else:
            self.vector_store = None
            raise FileNotFoundError(f"ChromaDB directory '{CHROMA_PATH}' not found. Please run the indexer first.")
        
    def recommend_jobs(self, resume_text, k=3, filters=None):
        """
        FR-2.3: Hybrid Search
        - resume_text: The query string
        - k: Number of results
        - filters: Dict for metadata filtering (e.g., {'location': 'New York'})
        """
        if not self.vector_store:
            raise ValueError("Vector store is not initialized.")
        
        
        active_filters = {k: v for k, v in filters.items() if v and v != "null"} if filters else {}
        if len(active_filters) > 1:
            chroma_filter = {
                "$and": [{key: value} for key, value in active_filters.items()]
            }
        elif len(active_filters) == 1:
            chroma_filter = active_filters
        else:
            chroma_filter = None
        print(f"🔍 Searching with filters: {chroma_filter}")
        results = self.vector_store.similarity_search_with_score(
            query=resume_text,
            k=k * 3,  # Fetch more to filter later
            filter=chroma_filter
        )
        # Format results
        jobs = []
        for doc, score in results:
            job_data = doc.metadata
            job_data['similarity_score'] = 1 - score # Convert distance to similarity (roughly)
            jobs.append(job_data)
            
        return jobs[:k]  # Return top k results
        
        
    
    def analyse_gap(self, resume_text, job_description):
        """
        FR-3: AI Reasoning Agent
        Uses Llama 3.1 to compare Resume vs Job Description.
        Returns strict JSON.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert Technical Recruiter. Compare the candidate's resume to the job description."),
            ("human", """
            JOB DESCRIPTION:
            {job_desc}
            
            CANDIDATE RESUME:
            {resume}
            
            TASK:
            1. Identify the Match Score (0-100%).
            2. List 3 Key Matching Skills.
            3. List 2 CRITICAL Missing Skills.
            4. Provide 1 specific advice to bridge the gap.
            
            Analyze the gap and return a JSON object with EXACTLY this structure:
            {{
                "match_score": "A number between 0-100",
                "matching_skills": ["skill1", "skill2"],
                "missing_skills": ["skill1", "skill2"],
                "advice": "1-2 sentences on how to improve."
            }}
            
            Return ONLY VALID JSON.
            """)
        ])

        chain = prompt | self.llm | JsonOutputParser()
        return chain.invoke({"job_desc": job_description, "resume": resume_text})
    def process_resume(self, file_path):
        """
        [OPTIMIZED] Single-Pass Extraction
        Uses 1 LLM Call to get:
        1. Metadata (Email)
        2. Filters (Location, Work Type)
        3. Refined Summary (Skills, Experience)
        """
        # 1. Parse PDF -> Raw Text
        parser = ResumeParser(file_path)
        raw_text = parser.extract_text()
        
        print("⚡ Processing resume (Single-Pass Extraction)...")
        
        prompt = ChatPromptTemplate.from_template(
            """
            You are an expert ATS (Applicant Tracking System).
            Analyze the following resume text and extract all key information into a strict JSON object.
            
            RESUME TEXT:
            {resume}
            
            REQUIRED JSON STRUCTURE:
            {{
                "user_email": "Extract the candidate's email (or null if not found)",
                "filters": {{
                    "location": "Preferred City/State (or null)",
                    "formatted_work_type": "Full-time, Part-time, or Contract (infer from context or null)"
                }},
                "summary": "A comprehensive summary of the candidate's key skills, technical stack, years of experience, and qualifications. This text will be used for vector embedding."
            }}
            """
        )
        
        chain = prompt | self.llm | JsonOutputParser()
        
        try:
            extracted_data = chain.invoke({"resume": raw_text})
            
            # Fallback: If LLM misses email, use Regex (It's free and fast)
            if not extracted_data.get("user_email"):
                extracted_data["user_email"] = parser.extract_email(raw_text)
            print(f"✅ Extraction Successful: {extracted_data}")
            return extracted_data
            
        except Exception as e:
            print(f"❌ Extraction Failed: {e}")
            # Fallback to raw text if LLM crashes
            return {
                "user_email": parser.extract_email(raw_text),
                "filters": {},
                "summary": raw_text 
            }
        
# Singleton instance
engine = SkillSyncEngine()

