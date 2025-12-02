import os
import json
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pdf_parser import ResumeParser


CHROMA_PATH = os.path.join("data", "jobs_db")
EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3.1"

class SkillSyncEngine:
    def __init__(self):
        print("Initializing SkillSyncEngine...")
        self.embedder = OllamaEmbeddings(model=EMBED_MODEL)
        self.llm = ChatOllama(model=LLM_MODEL, temperature=0, format="json")
        self.llm2 = ChatOllama(model=LLM_MODEL, temperature=0.3, format="text")
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
        1. Search vector DB for top K matches
        2. Return the raw job data
        """
        if not self.vector_store:
            raise ValueError("Vector store is not initialized.")

        print("Searching for similar job postings...")
        results = self.vector_store.similarity_search(
            query=resume_text,
            k=k
        )
        recommendations = []
        for doc in results:
            recommendations.append({
                "job_id": doc.metadata.get("job_id"),
                "company_name": doc.metadata.get("company_name"),
                "title": doc.metadata.get("title"),
                "location": doc.metadata.get("location"),
                "max_salary": doc.metadata.get("max_salary"),
                "pay_period": doc.metadata.get("pay_period"),
                "description_snippet": doc.page_content[:200],  # First 200 chars
                "job_description": doc.page_content
            })
        return recommendations
    
    def analyse_gap(self, resume_text, job_description):
        """
        Use LLM to analyze skill gaps between resume and job description.
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
            
            OUTPUT FORMAT:
            Score: [Score]%
            Matches: [Skill 1], [Skill 2], [Skill 3]
            Missing: [Skill 4], [Skill 5]
            Salary: [Salary Offered by the company]
            Salary Expectation: [Your expected salary based on market research in Rupees]
            Advice: [One sentence advice]
            """)
        ])

        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"job_desc": job_description, "resume": resume_text})
    def process_resume(self, file_path):
        """
        Process the resume text to extract key skills and information.
        This is a placeholder for any additional processing needed.
        """
        # For now, just return the cleaned resume text
        parser = ResumeParser(file_path)
        resume_text = parser.extract_text()
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert resume analyzer. Extract key skills and relevant information from the resume."),
            ("human", """
            CANDIDATE RESUME:
            {resume}
            
            TASK:
            Extract and summarize the key skills, experiences, and qualifications relevant to job applications.
            """)
        ])
        chain = prompt | self.llm2 | StrOutputParser()
        resume_text = chain.invoke({"resume": resume_text})
        print(f"Processed Resume Text: {resume_text}...")  # Print first 200 chars
        return resume_text
        
# Singleton instance
engine = SkillSyncEngine()

# --- Simple Test Block ---
if __name__ == "__main__":
    # Test with a dummy resume
    dummy_resume = engine.process_resume("sample_resume.pdf")
    
    recs = engine.recommend_jobs(dummy_resume, k=1)
    
    if recs:
        top_job = recs[0]
        print(f"\n🎯 Top Match: {top_job["title"]} at {top_job["company_name"]}")
        print(f"{top_job['job_description']}")
        
        print("\n🤖 Analyzing Gap...")
        analysis = engine.analyse_gap(dummy_resume, top_job['job_description'])
        print(analysis)