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
Your analysis must be meticulous, structured, visually well-formatted in Markdown, and tailored for legal professionals and academics.

⚖️ **Output Formatting Rules:**
- Use clear Markdown headings.
- Add 2–3 blank lines **before each major section heading**.
- Insert a horizontal divider (`---`) **before each major section** so the final document is visually separated.
- Always preserve numbering (1, 2, 3, etc.).
- Do not combine sections — every section must be clearly separated.

---

### 1. Case Docket
- **Case Title & Citation:** [Full Title and any available citation]
- **Court:** [Name of the Court]
- **Coram:** [The bench of judges, e.g., "J. D.Y. Chandrachud, J. A.S. Bopanna"]
- **Parties:**
  - Petitioner(s)/Appellant(s):
  - Respondent(s):
- **Date of Judgment:** [DD-MM-YYYY]

---

### 2. Legal Brief
- **Factual Matrix:** [A concise summary of the essential facts leading to the legal dispute.]
- **Arguments Advanced by Petitioner/Appellant:** [Bulleted list of the primary legal contentions.]
- **Arguments Advanced by Respondent:** [Bulleted list of the primary legal contentions.]
- **Issues Framed for Adjudication:** [The legal questions the court set out to decide.]
- **Holding & Final Order:** [The court's final decision and operative order, stated clearly.]
- **Ratio Decidendi:** [The core legal reasoning forming the basis of the decision. Explain the principle.]
- **Obiter Dicta (Noteworthy Observations):** [Any significant judicial observations not essential to the final decision.]

---

### 3. Case Timeline
**Instructions:** For each event, provide a short title and a detailed paragraph. Format it exactly like this:
- **[Date]:** [Short Event Title]
  - **Details:** [A detailed paragraph describing the event, its context, and its significance to the case.]
**Crucially, every single event listed MUST have both a title and a 'Details' section, even if the details are brief. Do not omit the 'Details:' line for any entry.**

---

### 4. Critical Analysis
- **Grounds for Appeal / Counter-Arguments:** [Provide 2–3 robust legal arguments that could form the basis of an appeal, a dissenting view, or a counter-argument from the losing side.]
- **Precedent Analysis:** [Comment on the application of 1–2 key cited cases. Were they followed, distinguished, or applied uniquely?]

---

### 5. Viva Voce & Study Guide
**Instructions:** Provide both the question and the correct answer immediately below it.

- **Multiple Choice Questions:**
  1. [Question 1]?
     - (A) ...
     - (B) ...
     - (C) ...
     - (D) ...
     - **Answer:** [(Correct Letter) - Brief explanation]
  2. [Question 2]?
     - **Answer:** ...
  3. [Question 3]?
     - **Answer:** ...

- **Short Answer Questions:**
  1. [Question 1]?
     - **Model Answer:** [Provide a concise, correct answer.]
  2. [Question 2]?
     - **Model Answer:** ...

---

### 6. Final Assessment
- **Plain English Summary:** [A simple summary for a non-legal audience.]

- **Argument Strength Score:**
Evaluate based on:
  1. Consistency of reasoning (0–25 points)
  2. Legal precedent alignment (0–25 points)
  3. Evidence strength (0–25 points)
  4. Clarity of ratio decidendi (0–25 points)

Provide:
- Final Score (e.g., SCORE: 82/100)
- Breakdown of each category in points
- A short 2–3 sentence justification for the score
Example:
SCORE: 82/100
- Consistency: 20/25
- Precedent: 21/25
- Evidence: 20/25
- Clarity: 21/25
Justification: The judgment is well-structured with solid precedent reliance but minor gaps in evidence reduce the score slightly.
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
