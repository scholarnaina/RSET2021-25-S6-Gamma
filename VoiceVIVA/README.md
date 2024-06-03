# VoiceVIVA 🎙️

Welcome to **VoiceVIVA** - an innovative interactive website designed to revolutionize the process of conducting VIVA (oral examination) assessments. Utilizing cutting-edge technology, VoiceVIVA enables users to respond to questions orally, with their answers automatically converted into text format for evaluation. This system offers a novel approach to assessing comprehension and knowledge retention, particularly in educational settings where oral examinations are prevalent.

## Features ✨

- **Test Module:**
  - 🎧 **Audio Questions & Answers:** Utilizes Gemini for generating questions and evaluating audio responses.
  - 📈 **Adaptive Difficulty:** Questions dynamically adjust based on user performance.
  - ⏱️ **Timed Responses:** Each question is timed to simulate real exam conditions.
  - 📝 **Personalized Feedback:** Provides detailed feedback and scores at the end of the test.
  - 📊 **Review & Analysis:** Review of answered questions with personalized feedback.
  - 🏆 **Leaderboard:** Compete with others and track your ranking.

- **Practice Module:**
  - ❓ **10 Questions:** Practice with a set of 10 questions without any time pressure.
  - 🎧 **Audio Questions & Answers:**  Questions are asked in audio format and answers are taken as audio and converted to text.
  - 💬 **Instant Feedback:** Receive immediate feedback after answering each question.
  - 📊 **Performance Report:** Get a personalized report and review at the end of the session.
  - 🤔 **Advanced Question Generation:** Generates questions from a PDF document using Spacy, NLTK, and TFIDF vectorizer.
  - 🧠 **Answer Evaluation:** Utilizes parallel processing with 7 threads, employing cosine similarity, keyword presence, and word similarity techniques.

## Tech Stack 🛠️

- **Backend:** Python, Flask
- **Libraries:** Spacy, NLTK, Scikit-learn, PyMuPDF, Pyttsx3, Transformers, Face Recognition, OpenCV
- **Frontend:** HTML, CSS, JavaScript


## Installation 🚀

Follow these steps to set up the project locally:

1. **Clone the repository:**
    ```bash
    git clone https://github.com/priya-anto-31/VoiceVIVA.git
    ```
2. **Navigate to the project directory:**
    ```bash
    cd VoiceVIVA
    ```
3. **Install dependencies:**
    Make sure you have `pip` installed, then run:
    ```bash
    pip install -r requirements.txt
    ```
4. **Run the application:**
    To start the application and access both the Test and Practice modules, execute the following command:
    ```bash
    python app.py
    ```
    Open your browser and go to `http://127.0.0.1:5000` to start using VoiceVIVA.

## Contributing 🤝

We welcome contributions from the community! If you encounter any bugs or have suggestions for improvements, feel free to open an issue or submit a pull request.

---

*Happy Learning with VoiceVIVA!* 🌟
