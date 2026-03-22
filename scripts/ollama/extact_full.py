import json
import base64
from io import BytesIO
from pydantic import BaseModel
from pdf2image import convert_from_path
import ollama

# 1. Define the exact structure (remains the same)
class GradeEntry(BaseModel):
    subject: str
    grade: str

class TranscriptData(BaseModel):
    student_name: str
    receiving_university: str
    grades: list[GradeEntry]

def process_transcript_vlm(file_path):
    print(f"📸 Converting PDF to images: {file_path}...")
    
    # Convert PDF pages to images (using 300 DPI for high OCR quality)
    # Note: Requires 'poppler-utils' installed on your system
    images = convert_from_path(file_path, dpi=300)
    
    # For a transcript, we usually want to process all pages. 
    # To keep it simple, we'll process the first page or combine them.
    # Here, we convert the first page to base64 for Ollama.
    buffered = BytesIO()
    images[0].save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    print("👁️ Sending image to Qwen3-VL for direct visual extraction...")

    # 2. Use Ollama with Qwen3-VL
    response = ollama.chat(
        model='qwen3-vl', # Ensure you have run 'ollama pull qwen3-vl'
        messages=[
            {
                'role': 'system',
                'content': 'You are a visual data extraction expert. Look at the transcript image and extract the requested fields precisely.'
            },
            {
                'role': 'user', 
                'content': 'Extract the student name, university, and the list of subjects with their grades from this transcript.',
                'images': [img_base64] # Passing the image directly
            }
        ],
        format=TranscriptData.model_json_schema(),
        options={'temperature': 0}
    )

    raw_content = response.message.content
    print(f"DEBUG: Raw model output: '{raw_content}'")

    if not raw_content:
        raise ValueError("The model returned an empty response. Check if the image is too large or the model is loaded.")

    return json.loads(raw_content)
    #return json.loads(response.message.content)

if __name__ == "__main__":
    # Path to your transcript
    path = "/home/espe/tfg/docs/tor/ESPERANTE RODRIGUEZ - RN.pdf"
    
    try:
        structured_json = process_transcript_vlm(path)
        print(json.dumps(structured_json, indent=2))
    except Exception as e:
        print(f"❌ Error: {e}")