import base64
import json
from io import BytesIO
from pdf2image import convert_from_path
import ollama

def extract_transcript_data(pdf_path):
    # 1. Convert PDF pages to images (using 300 DPI for high clarity)
    pages = convert_from_path(pdf_path, 300)
    
    extracted_data = []

    for i, page in enumerate(pages):
        # 2. Convert PIL Image to Base64
        print("Turn into image")
        buffered = BytesIO()
        page.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # 3. Define the Prompt & Schema
        prompt = """
        Analyze this transcript page. Extract the following information into a single JSON object:
        - student_name: Full name of the student.
        - receiving_university: Name of the institution.
        - grades: A list of objects containing 'subject' and 'grade'.
        
        If the information is not on this page, return an empty object for those fields.
        """

        # 4. Call Local VLM (Ollama)
        print("Call VLM")
        response = ollama.generate(
            model='qwen3-vl', #Default 8b 
            prompt=prompt,
            images=[img_base64],
            format='json',
            stream=False
        )

        page_json = json.loads(response['response'])
        extracted_data.append(page_json)
        print(f"Processed Page {i+1}")

    return extracted_data

# Run it
pdf = input()

results = extract_transcript_data(pdf)
print(json.dumps(results, indent=2))
