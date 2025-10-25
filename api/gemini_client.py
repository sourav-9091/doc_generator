from google import genai
import os

client = genai.Client(api_key="AIzaSyAR_rTt82yrIcxQCEmoLVNfK4MqAnJBZUk")

def generate_documentation(prompt: str) -> str:
    """
    Calls Google Gemini to generate SAP technical documentation.
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text
