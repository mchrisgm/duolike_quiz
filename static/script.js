const API_BASE_URL = "";

let score = 0;
let currentDifficulty = 1;

// Fetch a question
async function fetchQuestion(difficulty) {
  const response = await fetch(`${API_BASE_URL}/question?difficulty=${difficulty}`);
  const data = await response.json();
  return data;
}

// Post an answer
async function postAnswer(questionId, userAnswer) {
  const response = await fetch(`${API_BASE_URL}/answer`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ questionId, userAnswer }),
  });
  const data = await response.json();
  return data;
}

// Display a question
async function displayQuestion() {
  const questionData = await fetchQuestion(currentDifficulty);

  const fundName = document.getElementById("fund-name");
  const questionContainer = document.getElementById("question-container");
  const optionsContainer = document.getElementById("options-container");
  const answerInput = document.getElementById("user-answer");
  const submitAnswerButton = document.getElementById("submit-answer");
  const difficultyBar = document.querySelectorAll(".cell");

  fundName.textContent = `Fund: ${questionData.fund}`;
  questionContainer.innerHTML = `<p>${questionData.question}</p>`;
  optionsContainer.innerHTML = "";

  // Update difficulty bar
  difficultyBar.forEach((cell, index) => {
    cell.classList.toggle("active", index < currentDifficulty);
  });

  if (questionData.options) {
    // Hide input box for multiple-choice questions
    answerInput.style.display = "none";
    submitAnswerButton.style.display = "none";

    // Create multiple-choice buttons
    questionData.options.forEach((option) => {
      const button = document.createElement("button");
      button.textContent = option;
      button.addEventListener("click", () => checkAnswer(questionData.id, option));
      optionsContainer.appendChild(button);
    });
  } else {
    // Show input box for fill-in-the-blank questions
    answerInput.style.display = "block";
    submitAnswerButton.style.display = "block";
    answerInput.value = ""; // Clear previous input
    submitAnswerButton.onclick = () => checkAnswer(questionData.id, answerInput.value);
  }
}

// Show feedback pop-up
function showPopup(message, correct) {
  const popup = document.getElementById("popup-feedback");
  const popupMessage = document.getElementById("popup-message");
  popupMessage.textContent = message;
  popup.style.borderTopColor = correct ? "#4CAF50" : "#E53935";
  popup.classList.add("show");
}

// Hide feedback pop-up
function hidePopup() {
  const popup = document.getElementById("popup-feedback");
  popup.classList.remove("show");
}

// Check the answer
async function checkAnswer(questionId, userAnswer) {
  const result = await postAnswer(questionId, userAnswer);

  if (result.correct) {
    score += 10;
    showPopup(`Correct! Fact: ${result.fact}`, true);
  } else {
    showPopup(`Incorrect! Correct answer: ${result.correctAnswer || "N/A"}`, false);
  }

  const scoreValue = document.getElementById("score-value");
  scoreValue.textContent = score;

  if (score % 50 === 0 && currentDifficulty < 5) {
    currentDifficulty++;
  }
}

// Initialize the game
document.addEventListener("DOMContentLoaded", () => {
  const nextQuestionButton = document.getElementById("next-question");

  nextQuestionButton.addEventListener("click", () => {
    hidePopup();
    displayQuestion();
  });

  displayQuestion();
});
