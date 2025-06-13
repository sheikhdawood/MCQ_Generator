import os
import PyPDF2
import json
import traceback

def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader=PyPDF2.PdfReader(file)
            text=""
            for page in pdf_reader.pages:
                text+=page.extract_text()
            return text
            
        except Exception as e:
            raise Exception("error reading the PDF file")
        
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    
    else:
        raise Exception(
            "unsupported file format only pdf and text file suppoted"
            )
import json
import re
import traceback

def get_table_data(quiz_str):
    try:
        if not quiz_str or not quiz_str.strip():
            print("⚠️ Empty quiz_str")
            return None

        # Extract all individual JSON objects using regex
        json_objects = re.findall(r'({\s*".+?"\s*:\s*{.*?}})', quiz_str, re.DOTALL)

        if not json_objects:
            print("❌ No valid JSON objects found in the quiz string.")
            print("quiz_str:", quiz_str)
            return None

        # Merge all extracted JSON strings into one combined dictionary
        quiz_dict = {}
        for obj_str in json_objects:
            try:
                obj = json.loads(obj_str)
                quiz_dict.update(obj)
            except json.JSONDecodeError as err:
                print("⚠️ Skipping invalid object:", obj_str)
                print("Error:", err)

        quiz_table_data = []
        for key, value in quiz_dict.items():
            mcq = value.get("mcq", "")
            options = " || ".join([
                f"{opt} -> {text}" for opt, text in value.get("options", {}).items()
            ])
            correct = value.get("correct", "")
            quiz_table_data.append({
                "MCQ": mcq,
                "Choices": options,
                "Correct": correct
            })

        return quiz_table_data

    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return None
