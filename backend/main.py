# main.py
# backend/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import fitz, google.generativeai as genai, os # <-- Make sure 'os' is imported

app = FastAPI(title="LexAnalytica AI Backend")

# --- THIS IS THE FIX ---
# Load the key from an environment variable instead of hardcoding it
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("No GOOGLE_API_KEY set for Flask application")
# --- END OF FIX ---

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# ... (the rest of your main.py file stays the same)

# The list of allowed origins
origins = [
    "http://localhost:3000", # For local development
    "https://lex-analytica-app.vercel.app", # Your live frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# THE FIX: Numbers have been added back to the headings (e.g., ### 1. Case Docket)
PROMPT_V5_CORRECTED = """
You are an expert legal scholar AI specializing in the deconstruction of Indian judicial pronouncements.
Your output must be meticulous, visually well-formatted in Markdown, and complete — **no detail should be skipped**.

⚖️ **Critical Output Rules**
- Use clear Markdown headings.
- Always preserve numbering (### 1, ### 2, etc.).
- Add 3 blank lines before each major section heading.
- Add `***` (horizontal divider) after each major heading.
- Extract **all details even if they are scattered** in the judgment. Never write “N/A” without first searching the entire text.
- Each section should be complete and independent.

---

### 1. Case Docket
Include:
- **Case Title & Citation**
- **Court**
- **Coram** (Bench of Judges)
- **Parties:** Petitioner(s)/Appellant(s), Respondent(s)
- **Date of Judgment**

***\n\n\n***

### 2. Legal Brief
Include:
- **Factual Matrix** (facts + background + procedural history)
- **Arguments Advanced by Petitioner/Appellant** (each argument as a bullet)
- **Arguments Advanced by Respondent** (each argument as a bullet)
- **Issues for Adjudication**
- **Holding & Final Order**
- **Ratio Decidendi**
- **Obiter Dicta**

***\n\n\n***

### 3. Case Timeline
**Instructions:** For each event, provide a short title and a detailed paragraph. Format it exactly like this:
- **[Date]:** [Short Event Title]
  - **Details:** [A detailed paragraph describing the event, its context, and its significance to the case.]
**Crucially, every single event listed MUST have both a title and a 'Details' section, even if the details are brief. Do not omit the 'Details:' line for any entry.**

***\n\n\n***

### 4. Critical Analysis
- **Grounds for Appeal / Counter-Arguments**
- **Precedent Analysis** (applied, distinguished, overruled)

***\n\n\n***

### 5. Viva Voce & Study Guide
- **MCQs:** 3 questions with (A–D) + correct answer explained
- **Short Answer Questions:** 2 questions with concise model answers

***\n\n\n***

### 6. Final Assessment
- **Plain English Summary**
- **Argument Strength Score** (Breakdown: Consistency / Precedent / Evidence / Clarity — total 100)
Example:
SCORE: 82/100  
- Consistency: 20/25  
- Precedent: 21/25  
- Evidence: 20/25  
- Clarity: 21/25  
Justification: Judgment reasoning is strong and supported by precedent but minor factual omissions slightly lower the score.

***\n\n\n***

### 7. Key Statutes & Provisions
List each statute + section + provision summary + relevance.

***\n\n\n***

### 8. Precedents Cited
List each precedent with:
- **Case Name & Citation**
- **Court**
- **Application** (Followed, Distinguished, Overruled, Noted)

***\n\n\n***

### 9. Practical Implications
Summarize effects on:
- Legal procedure
- Rights of parties
- Industry/sector
- Future litigation

***\n\n\n***

### 10. Exam & Moot Court Relevance
- Key takeaways for law exams
- Moot court arguments supported by this judgment
- Hypothetical problem statements
"""


@app.post("/analyze-pdf/")
async def analyze_pdf_endpoint(files: list[UploadFile] = File(...)):
    full_text = ""
    for file in files:
        try:
            pdf_bytes = await file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            full_text += f"\n\n--- DOCUMENT: {file.filename} ---\n\n"
            full_text += "\n".join([page.get_text() for page in doc])
            doc.close()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing file {file.filename}: {e}")
    try:
        response = model.generate_content(PROMPT_V5_CORRECTED + full_text)
        return {"analysis": response.text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI model error: {e}")
