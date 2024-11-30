from flask import Flask, jsonify, request, send_from_directory
import random
import json

app = Flask(__name__, static_folder="static")

# Load JSON data
with open("combined_questions.json") as f:
    funds_data = json.load(f)

# Helper function to assign dynamic IDs to questions
def assign_question_ids(funds):
    question_id = 1
    for fund in funds:
        for question in fund["questions"]:
            question["id"] = question_id
            question_id += 1
    return funds

# Dynamically assign IDs to questions
funds_data = assign_question_ids(funds_data["funds"])

# Serve the main page
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

def clean_fund_name(fund_name):
    """Cleans and formats the fund name by removing unnecessary details."""
    # Remove dashes, dates, and file-specific details
    fund_name = fund_name.replace("Fund-Data-Fact-Sheet_", "").replace("Polar-Capital-Funds-plc-","").replace("_", " ").replace("-", " ")
    fund_name = " ".join(fund_name.split()[:-3])  # Remove the trailing date part
    return fund_name.strip()

# Updated function for serving a question
@app.route("/question", methods=["GET"])
def get_question():
    max_difficulty = int(request.args.get("difficulty", 1))
    difficulties = list(range(max_difficulty + 1))
    random.shuffle(difficulties)  # Randomize difficulties for fallback

    available_funds = funds_data[:]
    random.shuffle(available_funds)  # Randomize funds for selection

    # Iterate through funds and difficulties
    for fund in available_funds:
        for difficulty in difficulties:
            questions = [q for q in fund["questions"] if q["difficulty"] == difficulty]
            if questions:
                question = random.choice(questions)
                # Format the fund name nicely
                formatted_fund_name = clean_fund_name(fund["name"])
                return jsonify({
                    "id": question["id"],
                    "question": question["question"],
                    "options": question.get("options"),
                    "fund": formatted_fund_name,  # Use cleaned fund name
                })

    # If no questions found
    return jsonify({
        "error": "No questions available for the requested difficulty or funds.",
        "fund": "N/A",
        "question": "N/A",
    }), 200

# Validate an answer
@app.route("/answer", methods=["POST"])
def post_answer():
    data = request.json
    question_id = data.get("questionId")
    user_answer = data.get("userAnswer")

    for fund in funds_data:
        for question in fund["questions"]:
            if str(question["id"]) == str(question_id):
                correct = user_answer.strip().lower() == question["answer"].strip().lower()
                return jsonify({
                    "correct": correct,
                    "fact": question["fact"],
                    "correctAnswer": question["answer"]
                })
    return jsonify({
        "correct": False,
        "fact": "No fact available.",
        "correctAnswer": "No correct answer found."
    }), 404

# Serve static files (styles.css, script.js)
@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    app.run(debug=True)
