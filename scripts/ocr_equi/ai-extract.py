import pdfplumber
import json
import re

def extract_grade_conversions(pdf_path, output_json):
    all_data = {}
    current_country = None
    current_scale = None
    
    # regex to match the table rows precisely
    # Matches: [Source] [5-10] [1-4] [Literal Name]
    row_pattern = re.compile(
        r'^(\S+)\s+'                            # Source Grade
        r'([0-9,.]+)\s+'                        # Spanish 5-10
        r'([0-9,.]+)\s+'                        # Spanish 1-4
        r'(APROBADO|NOTABLE|SOBRESALIENTE|MATRICULA(?:[ \t]+DE[ \t]+HONOR)?)', 
        re.MULTILINE | re.IGNORECASE
    )

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            
            lines = text.split('\n')
            
            for i, line in enumerate(lines):
                # 1. FIX: Better Country & Scale identification
                if "Escala:" in line:
                    # Look back for country (uppercase, no admin keywords)
                    for j in range(i-1, -1, -1):
                        potential = lines[j].strip()
                        if potential.isupper() and "MINISTERIO" not in potential and "SECRETARÍA" not in potential:
                            current_country = potential
                            break
                    
                    # Extract Scale definition
                    scale_match = re.search(r"Escala:\s*(.*)", line)
                    current_scale = scale_match.group(1).strip() if scale_match else "Unknown Scale"

                    if current_country not in all_data:
                        all_data[current_country] = {"country": current_country, "scales": {}}
                    if current_scale not in all_data[current_country]["scales"]:
                        all_data[current_country]["scales"][current_scale] = []

                # 2. FIX: Robust value extraction using your successful Regex
                # We check lines that look like table rows
                match = row_pattern.match(line.strip())
                if match and current_country and current_scale:
                    all_data[current_country]["scales"][current_scale].append({
                        "source_value": match.group(1),
                        "spanish_equivalent_10": match.group(2),
                        "spanish_equivalent_4": match.group(3),
                        "spanish_equivalent_literal": match.group(4).strip()
                    })

    # Final Formatting: Convert dict to the required list structure
    final_output = []
    for c_name, c_info in all_data.items():
        scales_list = []
        for s_name, conversions in c_info["scales"].items():
            if conversions: # Only add scales that actually have data
                scales_list.append({
                    "scale_id": s_name,
                    "conversions": conversions
                })
        
        if scales_list:
            final_output.append({
                "country": c_name,
                "scales": scales_list
            })

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=4)

    print(f"Successfully saved to {output_json}")

# Usage: extract_grade_conversions('equiv-sample.pdf', 'output.json')
extract_grade_conversions('/home/espe/tfg/docs/equi-notas-Resolucion_20170918_Anexos.pdf', 'output.json')
