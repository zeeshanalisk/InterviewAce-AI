# 🎯 InterviewAce AI

**An AI-powered Interview Trainer Agent built for the IBM SkillsBuild Internship Program**

> Generate tailored interview questions, resume feedback, learning roadmaps, and career guidance — powered by **IBM Granite** via **IBM watsonx.ai**, with a built-in **RAG (Retrieval-Augmented Generation)** layer for role-specific knowledge.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Quick Start (Local)](#quick-start-local)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Customizing the Agent](#customizing-the-agent)
- [IBM Technology Used](#ibm-technology-used)
- [License](#license)

---

## Overview

InterviewAce AI is a complete interview preparation platform that uses **IBM Granite large language models** to deliver personalized, actionable career coaching. It follows a RAG pipeline: relevant context is first retrieved from a local knowledge base, then combined with the user's profile and sent to IBM Granite for generation.

**Built for:** IBM SkillsBuild Internship — Interview Trainer Agent submission.  
**Problem Statement Match:** AI Agent using IBM Cloud Lite + IBM watsonx.ai + IBM Granite.

---

## Features

| Feature | Description |
|---|---|
| 🎯 **Interview Preparation** | Role-specific questions, model STAR answers, and prep tips |
| 📄 **Resume Review** | AI critique, ATS optimization, rewritten bullets, score out of 10 |
| 🗺️ **Learning Roadmap** | Phase-by-phase plan with resources and IBM SkillsBuild certs |
| 🧭 **Career Guidance** | Answers any career question; includes salary negotiation advisor |
| 🔍 **RAG Layer** | TF-IDF retrieval from 6 local knowledge base files |
| ⚙️ **Agent Instructions** | Single file to customize tone, safety rules, and output format |
| 📥 **Download Outputs** | Every result can be saved as a `.txt` file |

---

## Architecture

```
User Input (Profile + Question)
        │
        ▼
┌───────────────────┐
│  RAG Retriever    │  ← TF-IDF search across knowledge_base/*.txt
│  (rag/retriever)  │
└────────┬──────────┘
         │  Retrieved Context
         ▼
┌───────────────────┐
│  Prompt Builder   │  ← Assembles system + user prompt
│  (core/prompts)   │
└────────┬──────────┘
         │  Full Prompt
         ▼
┌───────────────────┐
│  IBM Granite      │  ← ibm/granite-3-8b-instruct via watsonx.ai
│  (core/granite)   │
└────────┬──────────┘
         │  Generated Response
         ▼
   Streamlit UI Display
```

---

## Project Structure

```
interviewace_ai/
├── app.py                        # Main entry point — run this
├── requirements.txt
├── .env.example                  # Copy to .env with your credentials
│
├── core/
│   ├── agent_instructions.py     # ← Customize agent behavior HERE
│   ├── granite_client.py         # IBM watsonx.ai SDK connection
│   └── prompts.py                # All prompt templates
│
├── rag/
│   └── retriever.py              # TF-IDF retriever over knowledge base
│
├── knowledge_base/               # Local RAG knowledge files
│   ├── data_science.txt
│   ├── software_engineering.txt
│   ├── product_management.txt
│   ├── behavioral_hr.txt
│   ├── resume_tips.txt
│   └── general_career.txt
│
├── pages/
│   ├── interview_prep.py
│   ├── resume_review.py
│   ├── learning_roadmap.py
│   └── career_guidance.py
│
├── utils/
│   └── helpers.py                # Input validation, text utils, constants
│
└── .streamlit/
    └── config.toml               # Theme & server config
```

---

## Quick Start (Local)

### Prerequisites
- Python 3.10 or higher
- An [IBM Cloud](https://cloud.ibm.com) account (free Lite tier works)
- An [IBM watsonx.ai](https://dataplatform.cloud.ibm.com/) project

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/interviewace-ai.git
cd interviewace-ai/interviewace_ai
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Credentials

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
IBM_API_KEY=your_ibm_api_key_here
IBM_PROJECT_ID=your_watsonx_project_id_here
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
IBM_MODEL_ID=ibm/granite-3-8b-instruct
```

> 💡 **How to get these values:**
> - **IBM_API_KEY**: IBM Cloud → Manage → Access (IAM) → API Keys → Create
> - **IBM_PROJECT_ID**: watsonx.ai → Your project → Manage → General → Project ID
> - **IBM_WATSONX_URL**: Depends on your IBM Cloud region (usually `https://us-south.ml.cloud.ibm.com`)

### 5. Run the App

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

## Configuration

All IBM credentials are loaded from a `.env` file:

| Variable | Required | Description |
|---|---|---|
| `IBM_API_KEY` | ✅ | IBM Cloud API key |
| `IBM_PROJECT_ID` | ✅ | watsonx.ai project ID |
| `IBM_WATSONX_URL` | ✅ | watsonx.ai service URL |
| `IBM_MODEL_ID` | ✅ | Granite model ID |
| `LOG_LEVEL` | ❌ | Logging verbosity (default: INFO) |

### Recommended Model IDs

| Model | Best For |
|---|---|
| `ibm/granite-3-8b-instruct` | Best balance of speed and quality (recommended) |
| `ibm/granite-13b-instruct-v2` | Higher quality, slower |
| `ibm/granite-3-2b-instruct` | Fastest, lighter |

---

## Deployment

### Option A: Streamlit Community Cloud (Free, Recommended)

1. Push your project to a **public GitHub repository**.
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app.
3. Set **Main file path**: `interviewace_ai/app.py`
4. Under **Advanced settings → Secrets**, add your credentials:

```toml
WATSONX_APIKEY=Y1AQtqdUg9rhlJ2y_1QVllJf148M9ewEKibaJ2HvViqV
PROJECT_ID=ba687754-61ba-429d-a3be-de8054e90fba
URL=https://us-south.ml.cloud.ibm.com
MODEL_ID=ibm/granite-4-h-small
```

5. Click **Deploy** — your app will be live in ~2 minutes.

> ⚠️ **Never commit your `.env` file.** It is listed in `.gitignore`.  
> On Streamlit Cloud, use the Secrets manager instead.

### Option B: IBM Code Engine (Enterprise)

1. Build a Docker image:
```bash
docker build -t interviewace-ai .
```

2. Push to IBM Container Registry and deploy via IBM Code Engine.
3. Set environment variables in the Code Engine application settings.

### Option C: Local Network / LAN

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

---

## Customizing the Agent

Open [`core/agent_instructions.py`](core/agent_instructions.py) to change any of the following:

```python
# Change the agent's name and persona
AGENT_PERSONA = "..."

# Adjust tone rules (formal, casual, etc.)
TONE_RULES = "..."

# Add or relax safety guardrails
SAFETY_RULES = "..."

# Change output format (length, structure)
OUTPUT_FORMAT_RULES = "..."

# Feature-specific instructions for each section
INTERVIEW_PREP_INSTRUCTIONS = "..."
RESUME_REVIEW_INSTRUCTIONS = "..."
ROADMAP_INSTRUCTIONS = "..."
CAREER_GUIDANCE_INSTRUCTIONS = "..."

# Adjust Granite generation parameters
GENERATION_PARAMS = {
    "max_new_tokens": 1500,
    "temperature": 0.7,
    "top_p": 0.95,
    ...
}
```

### Adding Knowledge Base Content

Add a new `.txt` file to `knowledge_base/` — it will be automatically indexed by the RAG system on the next app start. No code changes needed.

---

## IBM Technology Used

| Component | IBM Product | Details |
|---|---|---|
| Language Model | **IBM Granite 3 8B Instruct** | `ibm/granite-3-8b-instruct` |
| AI Platform | **IBM watsonx.ai** | Cloud Lite tier |
| SDK | **ibm-watsonx-ai** Python SDK | v1.1.2+ |
| Cloud | **IBM Cloud (Lite)** | No cost tier |
| Learning | **IBM SkillsBuild** | Certifications referenced in roadmaps |

---

## License

This project is submitted as part of the **IBM SkillsBuild Internship Program**.  
For educational and evaluation purposes.

---

*Built with ❤️ using IBM Granite, IBM watsonx.ai, and Streamlit.*
