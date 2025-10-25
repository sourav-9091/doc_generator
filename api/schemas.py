from pydantic import BaseModel
from typing import List, Optional

class DocRequest(BaseModel):
    title: str
    prepared_by: str
    code_snippets: Optional[List[str]] = []
    error_descriptions: Optional[List[str]] = []
    chats_emails: Optional[List[str]] = []
    image_paths: Optional[List[str]] = []
    custom_command: Optional[List[str]] = []