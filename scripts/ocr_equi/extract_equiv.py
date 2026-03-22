import pdfplumber
import json
import re

def extract_grade_conversions(pdf_path):
    all_data = []
    current_country = None
    current_scale_data = None
    
    # regex to identify the Escala line
    escala_re = re.compile(r"Escala:\s*(.*)", re.IGNORECASE)
    # header detection to skip table headers on new pages
    header_keywords = ["Nota País", "Equivalente", "Origen", "Española"]

    with pdfplumber.open(pdf_path) as pdf:
        # Data typically starts after the index (Page 28 in this document)
        for page in pdf.pages[27:]: 
            text = page.extract_text()
            lines = text.split('\n')
            
            # Extract tables from the page
            table = page.extract_table()
            
            for row in (table or []):
                # Clean row data
                row = [cell.replace('\n', ' ').strip() if cell else "" for cell in row]
                
                # Check if this row defines a new country or scale
                row_text = " ".join(row)
                
                # 1. Detect Country Name (Usually single cell or first cell in uppercase)
                # In this PDF, countries appear as standalone lines or headers
                # We also look at the text above the table if table extraction misses it
                
                # 2. Detect Scale
                escala_match = escala_re.search(row_text)
                if escala_match:
                    # If we found a new scale, save the previous one if it exists
                    if current_scale_data:
                        save_scale(all_data, current_country, current_scale_data)
                    
                    current_scale_data = {
                        "scale_name": escala_match.group(1),
                        "conversions": []
                    }
                    continue

                # 3. Detect End of Equivalence
                if "FIN DE LA EQUIVALENCIA" in row_text:
                    if current_scale_data:
                        save_scale(all_data, current_country, current_scale_data)
                        current_scale_data = None
                    continue

                # 4. Extract Grade Data
                # Skip headers and empty rows
                if any(k in row_text for k in header_keywords) or not any(row):
                    continue
                
                # Verify we have a data row (usually 4 columns)
                if len(row) >= 4 and current_scale_data:
                    # Clean values: row[0]=Source, row[1]=Over 10, row[2]=Over 4, row[3]=Literal
                    try:
                        conversion = {
                            "source_value": row[0],
                            "spanish_10": row[1],
                            "spanish_4": row[2],
                            "literal": row[3]
                        }
                        current_scale_data["conversions"].append(conversion)
                    except IndexError:
                        continue

            # Contextual country detection if table extraction doesn't catch it
            # Usually the first few lines of a new section contain the country name
            for line in lines:
                if line.isupper() and "MINISTERIO" not in line and "DIRECCIÓN" not in line:
                    if not current_country or current_country != line.strip():
                        current_country = line.strip()
                    break

    return all_data

def save_scale(all_data, country_name, scale_data):
    # Find country in list or create new
    country_entry = next((c for c in all_data if c["country"] == country_name), None)
    if not country_entry:
        country_entry = {"country": country_name, "scales": []}
        all_data.append(country_entry)
    
    country_entry["scales"].append(scale_data)

# Execution
if __name__ == "__main__":
    pdf_file = "/home/espe/tfg/docs/equiv-sample-lite.pdf"
    results = extract_grade_conversions(pdf_file)
    
    with open("grade_conversions.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    print(f"Extraction complete. Data saved to grade_conversions.json")
