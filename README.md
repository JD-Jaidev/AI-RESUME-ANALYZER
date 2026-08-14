# 🤖 AI Resume Analyzer

An **AI-powered Multi model resume analysis tool** that compares a resume with a custom Job Description (JD) and provides an ATS-style score, skill matching, missing skills, and actionable improvement suggestions.

## 🚀 Features

- 📄 PDF resume upload
- 📝 Custom Job Description input
- 🤖 AI-powered resume analysis
- 📊 ATS score (0–100)
- ✅ Matching skills
- ❌ Missing skills
- 💡 Improvement suggestions
- 📋 Structured JSON output

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **LangChain**
- **LLM APIs (Gemini / other supported models)**
- **PyPDF2**
- **JSON & Regex**
- **python-dotenv**

## 📂 Project Structure

```text
AI-RESUME-ANALYZER/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env
└── faiss_index/
```

## ⚙️ Installation

### Clone the repository

```bash
git clone https://github.com/JD-Jaidev/AI-RESUME-ANALYZER
cd AI-RESUME-ANALYZER
```

### Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**Linux/macOS**

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure API Keys

Create a `.env` file and add the required API keys:

Only add the keys required by your implementation.

### Run the application

```bash
streamlit run app.py
```

## 🔄 WorkFlow

```text
Resume PDF
    ↓
PDF Text Extraction
    ↓
Resume Text + Job Description
    ↓
Prompt Template
    ↓
   LLM
    ↓
AI Resume/JD Analysis
    ↓
Structured JSON
    ↓
JSON Parsing
    ↓
ATS Score + Skills + Suggestions
    ↓
Streamlit UI
```

## 🔮 Future Improvements

* Model wise report comparison comparison
* Source/page references
* Improved retrieval and reranking
* Persistent vector database
* Multimodal document analysis
* Cloud deployment

## 👨‍💻 Author & Developer

**Jaidev S**

⭐ If you like the project, consider giving the repository a star !