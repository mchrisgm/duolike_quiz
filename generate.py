
import os
import json
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

client = OpenAI()

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def generate_questions_and_answers(pdf_text, fund_name):
    """Use OpenAI API to generate questions and answers for a given fund."""
    prompt = f"""You are a financial expert. Create a JSON structure containing a full set of questions and answers for the following fund information:

    Fund Name: {fund_name}
    Details: {pdf_text}

    Structure each question as follows:
    {{
        "type": "multiple_choice" or "fill_in_blank",
        "difficulty": 1 to 5,
        "question": "The question text",
        "options": ["Option 1", "Option 2", "Option 3", "Option 4"], # For multiple-choice questions
        "answer": "The correct answer",
        "fact": "A relevant fact about the answer"
    }}

    Provide at least 20 questions of varying difficulty, focusing on key facts, objectives, sectors, geography, and structure.
    Ensure the JSON follows this structure:
    {{
        "funds": [
            {{
                "name": "Fund Name",
                "details": {{
                    "objective": "Objective of the fund",
                    "base_currency": "Currency",
                    "fund_structure": "Structure",
                    "domicile": "Country",
                    "fund_size": "Size if available",
                    "launch_date": "Launch date if available",
                    "investment_manager": "Manager if available",
                    "sector_exposure": {{
                        "highest": "Highest sector",
                        "lowest": "Lowest sector"
                    }}
                }},
                "questions": [ ... questions ... ]
            }}
        ]
    }}

    Return ONLY the JSON object containing the questions and answers.
    Make sure there are exactly 20 questions.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a financial expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

def process_pdfs_in_folder(folder_path):
    """Process all PDF files in the given folder and generate individual JSON files."""
    json_outputs = []
    for file_name in sorted(os.listdir(folder_path)):
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, file_name)
            fund_name = os.path.splitext(file_name)[0]  # Using the file name as the fund name for simplicity
            output_json_path = os.path.splitext(pdf_path)[0] + "_questions.json"

            if os.path.exists(output_json_path):
                print(f"Skipping {file_name} as the output file already exists...")
                continue

            print(f"Processing {file_name}...")
            pdf_text = extract_text_from_pdf(pdf_path)
            qa_data = str(generate_questions_and_answers(pdf_text, fund_name))
            qa_data = qa_data.replace("```json\n", "").replace("```", "")  # Cleaning JSON formatting issues
            qa_data = json.loads(qa_data)  # Parse the JSON string

            # Save individual JSON file
            with open(output_json_path, "w") as output_file:
                json.dump(qa_data, output_file, indent=4)
            json_outputs.append(qa_data)

    return json_outputs

def main():
    client.api_key = os.getenv("OPENAI_API_KEY")
    input_folder = "data"
    output_combined_json = "combined_questions.json"

    print("Processing all PDF files in the folder...")
    json_outputs = process_pdfs_in_folder(input_folder)

    print("Combining all JSON outputs into one file...")
    combined_data = {"funds": []}
    for output in json_outputs:
        combined_data["funds"].extend(output["funds"])  # Combine all fund data

    # Save the combined JSON file
    with open(output_combined_json, "w") as combined_file:
        json.dump(combined_data, combined_file, indent=4)

    print(f"All questions and answers combined and saved to {output_combined_json}")

if __name__ == "__main__":
    main()
