import json
from pydantic import BaseModel
from docling.document_converter import DocumentConverter
import ollama

# 1. Define the exact structure you want using Pydantic
class GradeEntry(BaseModel):
    subject: str
    grade: str

class TranscriptData(BaseModel):
    student_name: str
    receiving_university: str
    grades: list[GradeEntry]

def process_transcript(file_path):
    print(f"📄 Parsing document: {file_path}...")
    
    # 2. Use Docling to convert PDF to Markdown
    # Docling automatically handles OCR for scanned pages
    converter = DocumentConverter()
    result = converter.convert(file_path)
    markdown_content = result.document.export_to_markdown()

    print("🧠 Sending to Local LLM for JSON extraction...")

    # 3. Use Ollama with Structured Output
    # We pass the Pydantic model schema directly to force valid JSON
    response = ollama.chat(
        model='qwen2.5', # Qwen 2.5 is excellent at following JSON schemas
        messages=[
            {
                'role': 'system',
                'content': 'You are a data extraction expert. Extract the student name, university, and all subjects/grades from the transcript.'
            },
            {
                'role': 'user', 
                'content': f"Extract the data from this transcript markdown:\n\n{markdown_content}"
            }
        ],
        format=TranscriptData.model_json_schema(), # Enforces the JSON structure
        options={'temperature': 0} # Set to 0 for maximum accuracy
    )

    # 4. Parse and return the result
    return json.loads(response.message.content)

# Run the pipeline
if __name__ == "__main__":
    path = "/home/espe/tfg/docs/tor/ESPERANTE RODRIGUEZ - RN.pdf"
    structured_json = process_transcript(path)
    print(json.dumps(structured_json, indent=2))
