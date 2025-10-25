from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from api.schemas import DocRequest
from api.gemini_client import generate_documentation
from api.doc_generator import create_word_doc
from fastapi.responses import FileResponse
import os

app = FastAPI(title="SAP Documentation Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend domain when deployed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# POST endpoint to generate doc
@app.post("/")
async def generate_doc(request: DocRequest):
    # Prepare prompt for Gemini
    prompt = f"""
    Here is the description for the documentation
    Technical Specification:
    Title: {request.title}
    Prepared By: {request.prepared_by}

    Code Snippets: {request.code_snippets}
    Error Descriptions: {request.error_descriptions}
    Chats / Emails: {request.chats_emails}
    custom command : {request.custom_command}

    Generate SAP Technical Documentation in the following format:

    Please provide sections: Purpose, Scope, Background, Root Cause Analysis, Design Solution, Objects Changed (table).

    Do not send the raw prompt as output keep it pointwise and tabular format when possible
    """

    # Call Gemini API
    doc_content = generate_documentation(prompt)

    txt_path = os.path.join(os.getcwd(), "SAP_Documentation.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(doc_content)


    doc_path = create_word_doc(request.title, request.prepared_by, doc_content, request.image_paths)

    return FileResponse(doc_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=os.path.basename(doc_path))
