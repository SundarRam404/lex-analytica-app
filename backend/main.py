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
Your output must be meticulous, visually well-formatted in Markdown, and complete — no detail should be missed.

⚖️ **Critical Output Rules**
- Use clear Markdown headings.
- Add 3 blank lines before each major section heading.
- Add a bold horizontal divider (`***`) after each section heading for strong visual separation.
- Preserve numbering of sections exactly (### 1, ### 2, etc.).
- Do not merge sections; each section must be fully separate.

---

### 1. Case Docket
Include:
- **Case Title & Citation:** [Full Title and any available citation]
- **Court:** [Name of the Court]
- **Coram:** [Bench of judges, e.g., "J. D.Y. Chandrachud, J. A.S. Bopanna"]
- **Parties:**
  - Petitioner(s)/Appellant(s)
  - Respondent(s)
- **Date of Judgment:** [DD-MM-YYYY]

***

### 2. Legal Brief
Include:
- **Factual Matrix:** [Concise summary of all facts leading to the legal dispute — include background, context, and procedural history]
- **Arguments Advanced by Petitioner/Appellant:** [All primary legal contentions; bullet every argument separately]
- **Arguments Advanced by Respondent:** [All primary legal contentions; bullet every argument separately]
- **Issues Framed for Adjudication:** [Enumerate all legal issues court addressed]
- **Holding & Final Order:** [Court's final decision and operative order, stated clearly]
- **Ratio Decidendi:** [Core legal reasoning forming the basis of the decision. Explain principle in detail]
- **Obiter Dicta:** [Any significant judicial observations not essential to decision]

***

### 3. Case Timeline
**Extract EVERY procedural and factual event in the judgment that has a date or sequence of actions.**
- Search entire judgment for all **dates**, procedural steps, and factual events — do not skip any.
- Include events such as: case filing, hearings, appeals, orders, adjournments, notices, evidence submissions, arguments, judgment delivery.
- Format exactly:
  - **[Date]:** [Short Title]
    - **Details:** [Detailed explanation of what occurred and its legal significance]

***

### 4. Critical Analysis
Include:
- **Grounds for Appeal / Counter-Arguments:** [2–3 robust legal arguments that could form basis of appeal or dissent]
- **Precedent Analysis:** [Application of 1–2 key cited cases: whether followed, distinguished, or uniquely applied]

***

### 5. Viva Voce & Study Guide
**Output both the question and the correct answer.**
- **Multiple Choice Questions:** 3 MCQs with options (A–D) + correct answer explained
- **Short Answer Questions:** 2 short questions with concise, model answers

***

### 6. Final Assessment
- **Plain English Summary:** [Simple explanation for a non-legal audience]
- **Argument Strength Score:**
  - Evaluate using:
    - Consistency of reasoning (0–25 points)
    - Legal precedent alignment (0–25 points)
    - Evidence strength (0–25 points)
    - Clarity of ratio decidendi (0–25 points)
  - Provide:
    - Final Score (e.g., SCORE: 82/100)
    - Breakdown for each criterion
    - Justification in 2–3 sentences
Example:
SCORE: 82/100
- Consistency: 20/25
- Precedent: 21/25
- Evidence: 20/25
- Clarity: 21/25
Justification: Judgment reasoning is strong, consistent, and supported by precedent, but minor factual gaps reduce the total.

***

### 7. Key Statutes & Provisions
- List all statutes, sections, and clauses referenced in the judgment.
- For each, provide:
  - **Section:** Number & name
  - **Provision summary:** In plain English
  - **Relevance:** Why it matters in this case

  ***

  ### 8. Precedents Cited
- List each precedent with:
  - **Case Name & Citation**
  - **Court**
  - **How it was applied:** Followed, Distinguished, Overruled, or Noted

   ***

   ### 9. Practical Implications
- Summarize how this judgment impacts:
  - Legal procedure
  - Rights of parties
  - Industry/sector (if applicable)
  - Future cases

  ***

  ### 10. Exam & Moot Court Relevance
- Key takeaways for law exams
- Possible moot court arguments this judgment supports
- Hypothetical questions based on this judgment
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
        return {"analysis": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI model error: {e}")
