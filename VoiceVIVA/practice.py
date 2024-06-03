from flask import Blueprint
from flask import Flask, render_template, request, jsonify, send_file , redirect, url_for, session
import requests
import speech_recognition as sr
import pyttsx3
import os
import time
import qgen
import random
import answerGeneration
import answerChecking

practice_bp = Blueprint('practice', __name__)

practice_bp.secret_key = 'PRACTICE_SECRET_KEY'


num_questions = 10  # Set the number of questions needed
question_extractor = qgen.QuestionExtractor(num_questions)

# Provide the path to your PDF file
pdf_path = "static/DATA STRUCTURES NOTES.pdf"
feedback_message=['The answer that you have provided is correct. Well done!','Your answer is the correct answer.','You need to improve. Your answer is partially correct.','Your answer is incorrect. Please practice and try again.']

# Define a flag to control question generation
generating_question = False


# Define API keys and global variables
ss_api = 'YOUR_API_KEY'
current_question_index = 0
questions = []
questions_order=[]
user_answers = []
correctans=[]
ans=[]
question_answers = [[] for _ in range(10)]
x=''
sum=0


# Store the start time of the quiz
quiz_start_time = None

# Define base URL for Gemini API
base_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=' + ss_api

@practice_bp.route('/practice')
def practice():
    email = session.get('email')
    return render_template('indexp.html', email=email) 

# Function to make requests to Gemini API
def make_gemini_request(prompt, method='POST'):
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    url = base_url
    try:
        response = requests.post(url, json=data, headers=headers)
        return response.json()
    except requests.exceptions.RequestException as e:
        return None

# Route to generate a question
def generate_question_audio(question_text, question_index):
    engine = pyttsx3.init()
    engine.save_to_file(question_text, f'static/question_{question_index}.mp3')
    engine.runAndWait()
   
# Get questions from the PDF document
questions = question_extractor.get_questions_from_pdf(pdf_path)

# Shuffle the questions to get random order
random.shuffle(questions)
questions_order = questions[:num_questions]
ans=answerGeneration.generate_answers(questions_order)
correctans = [value[0] for value in ans.values()]
# count=0

@practice_bp.route('/generate_question_p')
def generate_questions():
    global question_extractor, current_question_index, questions_order, random_question, first_elements, ans, a

    # Check if current_question_index is within bounds
    if current_question_index < len(questions_order):
        # Select a random question from the list
        random_question = questions_order[current_question_index]
        generate_question_audio(random_question, current_question_index+1)
        first_elements = [value[0] for value in ans.values()]
        a = first_elements[current_question_index]

        current_question_index += 1
        # Return the random question as JSON
        return jsonify({'question': random_question, 'answers': a})
    else:
        return jsonify({'error': 'All questions have been generated'})


answer = ""

# Route to evaluate user answer
@practice_bp.route('/evaluate_answer_p', methods=['POST'])
def evaluate_answer():
    global current_question_index,answer,mark,sum,random_question,a
    data = request.get_json()
    user_answer = data.get('user_answer')
    # Set user answer to an empty string if it's None
    if user_answer is None:
        user_answer = ""
    
    overall_score = answerChecking.process_answers(a, user_answer)
    
    print("Overall Score:", overall_score)
    if overall_score>4.8:
        feedback=feedback_message[0]
    elif overall_score>4:
        feedback=feedback_message[1]
    elif overall_score>3:
        feedback=feedback_message[2]
    elif overall_score<3:
        feedback=feedback_message[3]

    if 'sum' not in globals():
        sum = 0
        mark=0
         
    sum+=overall_score

    
    correct_answer = correctans[current_question_index-1]

    feedback += "\nThe correct answer is: \n" + correct_answer 

    entry = random_question, {'user_answer': user_answer, 'feedback': feedback,'score': overall_score}
    question_answers[current_question_index - 1] = entry

    return jsonify({'user_answer':user_answer,'feedback':feedback,'correct_answer':correct_answer,'overall_score': overall_score})


# Route to fetch question audio
@practice_bp.route('/question_audio_p')
def question_audio():
    global current_question_index
    if current_question_index <=10 :
        question_audio_path = f'static/question_{current_question_index}.mp3'
        if os.path.exists(question_audio_path):
            return send_file(question_audio_path, as_attachment=True)
    return jsonify({'error': 'Question audio not found'})


# Route to receive subjects that need improvement and generate personalized feedback
@practice_bp.route('/improve_subjects_p', methods=['POST'])
def improve_subjects():
    global final_score
    data = request.get_json()
    improve = data.get('improve', [])

    personalized_feedback = []
    # Loop through the subjects that need improvement and generate personalized feedback for each subject
    for subject in improve:
        prompt = f"Provide a small personalized feedback on how to improve in {subject}."
        feedback_response = make_gemini_request(prompt)
        if feedback_response and 'candidates' in feedback_response:
            feedback_text = feedback_response['candidates'][0]['content']['parts'][0]['text']
            personalized_feedback.append(feedback_text)

    # Combine all personalized feedback messages into a single string
    combined_feedback = '\n'.join(personalized_feedback)
    return jsonify({'personalized_feedback': combined_feedback})

# Route to calculate final score
@practice_bp.route('/final_score_p')
def calculate_final_score():
    global mark, quiz_start_time, question_answers, final_score,correctans
    final_score = sum if 'sum' in globals() else 0
    for i in range(10):
        # Check if the list is empty at the current index
        if not question_answers[i]:
            # Fill in the skipped question with default values
            entry = [questions_order[i], {'user_answer': "You have not provided any answer", 
                                    'feedback': "The correct answer is: \n"+correctans[i], 
                                    'score': '0/5'}]
            question_answers[i] = entry
    return jsonify({'final_score': final_score,'question_answers':question_answers})

