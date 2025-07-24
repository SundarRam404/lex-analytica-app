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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# THE FIX: Numbers have been added back to the headings (e.g., ### 1. Case Docket)
PROMPT_V5_CORRECTED = """
You are to act as an expert legal scholar AI, specializing in the deconstruction of Indian judicial pronouncements. Your analysis must be meticulous, structured, and tailored for legal professionals and academics.

From the provided court judgment text, generate a comprehensive report structured with the following sections using clear Markdown formatting.

### 1. Case Docket
- **Case Title & Citation:** [Full Title and any available citation]
- **Court:** [Name of the Court]
- **Coram:** [The bench of judges, e.g., "J. D.Y. Chandrachud, J. A.S. Bopanna"]
- **Parties:**
  - Petitioner(s)/Appellant(s):
  - Respondent(s):
- **Date of Judgment:** [DD-MM-YYYY]

### 2. Legal Brief
- **Factual Matrix:** [A concise summary of the essential facts leading to the legal dispute.]
- **Arguments Advanced by Petitioner/Appellant:** [Bulleted list of the primary legal contentions.]
- **Arguments Advanced by Respondent:** [Bulleted list of the primary legal contentions.]
- **Issues Framed for Adjudication:** [The legal questions the court set out to decide.]
- **Holding & Final Order:** [The court's final decision and operative order, stated clearly.]
- **Ratio Decidendi:** [The core legal reasoning forming the basis of the decision. Explain the principle.]
- **Obiter Dicta (Noteworthy Observations):** [Any significant judicial observations not essential to the final decision.]

### 3. Case Timeline
**Instructions:** For each event, provide a short title and a detailed paragraph. Format it exactly like this:
- **[Date]:** [Short Event Title]
  - **Details:** [A detailed paragraph describing the event, its context, and its significance to the case.]
**Crucially, every single event listed MUST have both a title and a 'Details' section, even if the details are brief. Do not omit the 'Details:' line for any entry.**

### 4. Critical Analysis
- **Grounds for Appeal / Counter-Arguments:** [Provide 2-3 robust legal arguments that could form the basis of an appeal, a dissenting view, or a counter-argument from the losing side.]
- **Precedent Analysis:** [Comment on the application of 1-2 key cited cases. Were they followed, distinguished, or applied uniquely?]

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

### 6. Final Assessment
- **Plain English Summary:** [A simple summary for a non-legal audience.]
- **Argument Strength Score:** [Provide a numerical score out of 100 for the judgment's reasoning, followed by a newline and a 2-3 sentence justification. The entire output for this section must begin with the format: SCORE: 85/100]
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