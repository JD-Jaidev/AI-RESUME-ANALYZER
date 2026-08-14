import streamlit as st
from PyPDF2 import PdfReader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os
import json
import re
from dotenv import load_dotenv

# Load environment variables (API Keys from .env)
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

if not google_api_key:
    google_api_key = st.secrets.get("GOOGLE_API_KEY")

if not openrouter_api_key:
    openrouter_api_key = st.secrets.get("OPENROUTER_API_KEY")

def get_pdf_text(pdf_file):
    # Extracts text from the uploaded PDF resume.
    text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def get_analyzer_model(model_choice):
    # Dynamically loads the selected LLM.
    if model_choice == "Titan 3.5":
        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            google_api_key=google_api_key,
            temperature=0.1
        )
    else:
        MODELS = {
            "Kairo V3": "deepseek/deepseek-chat",
            "Luma 3": "qwen/qwen3-8b"
        }
        model = ChatOpenAI(
            model=MODELS[model_choice],
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_api_key,
            temperature=0.1
        )
    return model

def analyze_resume(resume_text, jd_text, model_choice):
    """Passes the full resume and JD to the LLM to get a structured JSON evaluation."""
    model = get_analyzer_model(model_choice)
    
    prompt_template = """
    You are an expert Applicant Tracking System (ATS) and Senior Tech Recruiter.
    Your task is to thoroughly evaluate the provided Resume against the target Job Description (JD).
    
    Job Description:
    {jd_text}
    
    Resume:
    {resume_text}
    
    Provide your evaluation STRICTLY as a JSON object with the following exact keys. Do not include any other text, markdown blocks, or explanations outside the JSON format.
    {{
        "ats_score": <an integer between 0 and 100 representing the match percentage>,
        "summary": "<a 2-3 sentence summary of the candidate's overall fit for the role>",
        "matching_skills": [<array of strings containing key skills present in both the JD and resume>],
        "missing_skills": [<array of strings containing key skills required by the JD but missing in the resume>],
        "points_to_improve": [<array of strings containing actionable advice to tailor the resume for this specific JD>]
    }}
    """
    
    prompt = PromptTemplate(template=prompt_template, input_variables=["jd_text", "resume_text"])
    chain = prompt | model
    
    # We use invoke instead of stream because we need the complete JSON to render the dashboard
    response = chain.invoke({"jd_text": jd_text, "resume_text": resume_text})
    return response.content

def main():
    st.set_page_config(page_title="AI ATS Resume Analyzer", page_icon="📈", layout="centered")
    
    st.title("📈 AI Resume Analyzer")
    col1, col2 = st.columns([1, 3])
    with col1:
        model_choice = st.selectbox(
            "Select AI Model",
            ("Titan 3.5", "Kairo V3", "Luma 3"),
            index=1,
            label_visibility="collapsed"
        )

    st.caption(f"Currently active model : **{model_choice}**")
    st.divider()

    # Layout: Upload Resume and Paste JD side-by-side
    col_upload, col_jd = st.columns(2)
    
    with col_upload:
        st.subheader("1. Upload Resume")
        pdf_doc = st.file_uploader("Upload your Resume (PDF format)", accept_multiple_files=False, type=["pdf"])
        
    with col_jd:
        st.subheader("2. Target Job Description")
        jd_text = st.text_area("Paste the Job Description here", height=200, placeholder="E.g., We are looking for a software engineer with experience in Python, Streamlit, and GenAI...")

    if st.button("Analyze ATS Compatibility", use_container_width=True, type="primary"):
        if not pdf_doc:
            st.warning("Please upload a resume (PDF).")
        elif not jd_text.strip():
            st.warning("Please paste a target Job Description.")
        else:
            with st.spinner(f"{model_choice} is analyzing your resume against the JD..."):
                try:
                    resume_text = get_pdf_text(pdf_doc)
                    response_text = analyze_resume(resume_text, jd_text, model_choice)
                    
                    # Regex to strip markdown code fences in case the LLM includes them
                    clean_text = re.sub(r'```(?:json)?\n?(.*?)\n?```', r'\1', response_text, flags=re.DOTALL).strip()
                    analysis_result = json.loads(clean_text)
                    
                    st.success("Analysis Complete!")
                    st.divider()
                    
                    # --- Dashboard Visualization ---
                    st.header("📊 ATS Analysis Report")
                    
                    score_col, summary_col = st.columns([1, 2])
                    
                    with score_col:
                        score = analysis_result.get("ats_score", 0)
                        # Metric and Progress Bar for visualization
                        st.metric(label="ATS Match Score", value=f"{score}%")
                        st.progress(score / 100)
                        
                        if score >= 80:
                            st.success("Excellent Match! Highly likely to pass ATS screening.")
                        elif score >= 60:
                            st.warning("Good Match. Consider adding the missing keywords below.")
                        else:
                            st.error("Low Match. Significant resume tailoring required.")
                            
                    with summary_col:
                        st.subheader("Executive Summary")
                        st.write(analysis_result.get("summary", "No summary provided."))
                        
                    st.divider()
                    
                    # Detailed Breakdown
                    skills_col1, skills_col2 = st.columns(2)
                    
                    with skills_col1:
                        st.subheader("✅ Matching Skills")
                        for skill in analysis_result.get("matching_skills", []):
                            st.markdown(f"- {skill}")
                            
                    with skills_col2:
                        st.subheader("❌ Missing Skills")
                        for skill in analysis_result.get("missing_skills", []):
                            st.markdown(f"- {skill}")
                            
                    st.divider()
                    
                    st.subheader("💡 Points to Improve")
                    for point in analysis_result.get("points_to_improve", []):
                        st.info(point)
                        
                except json.JSONDecodeError:
                    st.error("Failed to parse the AI response format. Please try again.")
                    with st.expander("Raw AI Output"):
                        st.write(response_text)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()