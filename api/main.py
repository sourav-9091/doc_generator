from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import os
from api.gemini_client import generate_documentation
from api.doc_generator import create_word_doc

# -------------------------
# Schemas
# -------------------------
class DocRequest(BaseModel):
    title: str
    prepared_by: str
    code_snippets: list = []
    error_descriptions: list = []
    chats_emails: list = []
    custom_command: list = []
    image_paths: list = []

# -------------------------
# App Initialization
# -------------------------
app = FastAPI(title="SAP Documentation Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Helper function
# -------------------------
def sanitize_generated_content(generated_text: str) -> str:
    """
    Removes unwanted sections and raw prompts.
    Keeps only: Purpose, Scope, Background, Root Cause Analysis, Design Solution, Objects Changed
    """
    allowed_sections = ["Purpose", "Scope", "Background", "Root Cause Analysis", "Design Solution", "Objects Changed"]
    lines = generated_text.splitlines()
    sanitized_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if any(line.startswith(f"**{section}") for section in allowed_sections):
            sanitized_lines.append(line)
        elif sanitized_lines and not line.startswith("**"):
            sanitized_lines.append(line)
    return "\n".join(sanitized_lines)

# -------------------------
# API Endpoint
# -------------------------
@app.post("/")
async def generate_doc(request: DocRequest):
    try:
        # 1. Prepare prompt
        prompt = f"""
        Here is the description for the documentation
        Technical Specification:
        Title: {request.title}
        Prepared By: {request.prepared_by}

        Code Snippets: {request.code_snippets}
        Error Descriptions: {request.error_descriptions}
        Chats / Emails: {request.chats_emails}
        Custom Command: {request.custom_command}

        Generate SAP Technical Documentation in the following format:
        Sections: Purpose, Scope, Background, Root Cause Analysis, Design Solution, Objects Changed (table).
        """

        # 2. Call Gemini API
        doc_content = generate_documentation(prompt)

        if not doc_content or doc_content.strip() == "":
            raise HTTPException(status_code=500, detail="Gemini API returned empty content")

        # 3. Sanitize content
        sanitized_content = sanitize_generated_content(doc_content)

        # 4. Save TXT file for reference
        txt_path = os.path.join(os.getcwd(), f"{request.title.replace(' ', '_')}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(sanitized_content)

        # 5. Create Word doc
        doc_path = create_word_doc(request.title, request.prepared_by, sanitized_content, request.image_paths)

        # 6. Return Word file
        return FileResponse(
            doc_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=os.path.basename(doc_path)
        )

    except Exception as e:
        # Return error info in JSON
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )
