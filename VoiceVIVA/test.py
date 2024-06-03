from flask import Blueprint, render_template
from flask import Flask, render_template, request, jsonify, send_file , redirect, url_for, session
import requests
import speech_recognition as sr
import pyttsx3
import os
import time

test_bp = Blueprint('test', __name__)

@test_bp.route('/test')
def test():
    email = session.get('email')
    return render_template('index1.html', email=email)


test_bp.secret_key = 'TEST_SECRET_KEY'

# Define a flag to control question generation
generating_question = False


@test_bp.route('/leaderBoard')
def leaderboard():
    email = session.get('email')
    return render_template('leaderBoard.html', email=email)


api_key = 'YOUR_API_KEY'
api_key2 = 'YOUR_API_KEY'
api_secret = 'YOUR_API_KEY'
ss_api = 'YOUR_API_KEY'
current_question_index = 0
questions = []
question_answers = [[] for _ in range(5)]  
correct_answer=[]
user_answers = []
x=''
topics=['arrays','linked lists','stacks and queues','trees and graphs','hashing and heaps']
diff=['Easy','Medium','Hard']

# Store the start time of the quiz
quiz_start_time = None

# Define base URL for Gemini API
base_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=' + ss_api

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

# Route to generate a question
@test_bp.route('/generate_question')
def generate_question():
    global current_question_index, k, generating_question, d, quiz_start_time,g_answer,gemini_answer
    # Start the timer when the quiz begins
    if quiz_start_time is None:
        quiz_start_time = time.time()  # Record the current time as the start time of the quiz
    if not generating_question and current_question_index < 5:
        generating_question = True
        if 'k' not in globals():
            k = 0  
            d = 0
        try:
            question_response = make_gemini_request("Ask an "+diff[d]+" one line question(without answer) about data structures(don't ask time complexity questions) only from the topic "+topics[k])
            print(topics[k],diff[d])
            k += 1
            try:
                question_text = question_response['candidates'][0]['content']['parts'][0]['text']
                questions.append(question_text)
                
                correct=make_gemini_request(f"Generate answer for the question: {question_text}")
                if correct and 'candidates' in correct:
                    gemini_answer = correct['candidates'][0]['content']['parts'][0]['text']
                correct_answer.append(gemini_answer)

                current_question_index += 1
                generate_question_audio(question_text, current_question_index)
                generating_question = False 
                return jsonify({'question': question_text,'difficulty': diff[d]})  # Return the question text
            except IndexError:
                generating_question = False
                return jsonify({'error': 'Unable to access question text'})
        except requests.exceptions.RequestException as e:
            generating_question = False
            return jsonify({'error': 'Unable to generate question'})
    else:
        return jsonify({'error': 'Question generation in progress or quiz completed'})

#Adjust difficulty
def adjust_difficulty():
    global d
    if mark<=2:
        if d==1:
            d=0
        elif d==2:
            d=1
    elif mark>3:
        if d==0:
            d=1
        elif d==1:
            d=2

# Route to evaluate user answer
@test_bp.route('/evaluate_answer', methods=['POST'])
def evaluate_answer():
    global current_question_index, sum, mark,question_answers,g_answer,gemini_answer
    data = request.get_json()
    user_answer = data.get('user_answer')

    # Set user answer to an empty string if it's None
    if user_answer is None:
        user_answer = ""
 
    evaluation_response = make_gemini_request(f"Evaluate the correctness of following answer: {user_answer} for the question: {questions[current_question_index - 1]}. Provide the correct answer for the {questions[current_question_index - 1]}.")
    evaluation_score = make_gemini_request(f"Assign a score out of 5 for the following answer: {user_answer} to the question: {questions[current_question_index - 1]} based on its correctness")

    if not evaluation_response or 'candidates' not in evaluation_response:
        return jsonify({'error': 'Unable to evaluate answer'})
    if not evaluation_score or 'candidates' not in evaluation_score:
        return jsonify({'error': 'Unable to evaluate answer'})
    
    score = evaluation_score['candidates'][0]['content']['parts'][0]['text']
    feedback = evaluation_response['candidates'][0]['content']['parts'][0]['text']

    entry = [questions[current_question_index - 1], {'user_answer': user_answer, 'feedback': feedback, 'score': score}]
    question_answers[current_question_index - 1] = entry

    if 'sum' not in globals():
        sum = 0
        mark=0
        
    for x in score:              #extracting the first digit bcoz that will be the score
        if x.isdigit():
            break   
         
    sum+=int(x)
    mark=int(x)
    print(mark)
    adjust_difficulty()
    return jsonify({'feedback': feedback, 'score': sum, 'mark': mark})

# Route to fetch question audio
@test_bp.route('/question_audio')
def question_audio():
    global current_question_index
    if current_question_index <= 5:
        question_audio_path = f'static/question_{current_question_index}.mp3'
        if os.path.exists(question_audio_path):
            return send_file(question_audio_path, as_attachment=True)
    return jsonify({'error': 'Question audio not found'})

# Route to receive subjects that need improvement and generate personalized feedback
@test_bp.route('/improve_subjects', methods=['POST'])
def improve_subjects():
    global final_score
    print(final_score)
    data = request.get_json()
    improve = data.get('improve', [])

    prompt = f"Provide a small motivational message and review as a paragraph based on my performance in this viva"
    small_feedback = make_gemini_request(prompt)
    if small_feedback and 'candidates' in small_feedback:
        small_feedback_text = small_feedback['candidates'][0]['content']['parts'][0]['text']

    personalized_feedback = []
    # Loop through the subjects that need improvement and generate personalized feedback for each subject
    for subject in improve:
        prompt = f"Provide a very small personalized feedback on how to improve in {subject}."
        feedback_response = make_gemini_request(prompt)
        if feedback_response and 'candidates' in feedback_response:
            feedback_text = feedback_response['candidates'][0]['content']['parts'][0]['text']
            personalized_feedback.append(feedback_text)

    # Combine all personalized feedback messages into a single string
    combined_feedback = '\n'.join(personalized_feedback)
    return jsonify({'personalized_feedback': combined_feedback,'small_feedback':small_feedback_text})

# Route to calculate final score
@test_bp.route('/final_score')
def calculate_final_score():
    global mark, quiz_start_time, question_answers, final_score,sum
    final_score = sum if 'sum' in globals() else 0
    # Iterate through question_answers
    for i in range(len(question_answers)):
        # Check if the list is empty at the current index
        if not question_answers[i]:
            # Fill in the skipped question with default values
            entry = [questions[i], {'user_answer': "You have not provided any answer", 
                                    'feedback': "The correct answer is: \n"+correct_answer[i], 
                                    'score': '0/5'}]
            question_answers[i] = entry
    return jsonify({'final_score': final_score,'question_answers':question_answers,'questions_content':questions,'correct_answer':correct_answer})

# Add a route to start the timer when the quiz starts
@test_bp.route('/start_timer', methods=['GET'])
def start_timer():
    global quiz_start_time,sum
    final_score = sum if 'sum' in globals() else 0
    if quiz_start_time is not None:
        total_time_seconds = int(time.time() - quiz_start_time)  # Calculate the total time in seconds
        return jsonify({'final_score': final_score, 'total_time_seconds': total_time_seconds})
    else:
        return jsonify({'error': 'Timer not started'})
    quiz_start_time = time.time()  # Record the current time as the start time of the quiz
    return jsonify({'message': 'Timer started'})

# Add a route to stop the timer and calculate the total time when the quiz ends
@test_bp.route('/stop_timer', methods=['GET'])
def stop_timer():
    global quiz_start_time
    if quiz_start_time is not None:
        total_time_seconds = int(time.time() - quiz_start_time)  # Calculate the total time in seconds
        return jsonify({'total_time_seconds': total_time_seconds})
    else:
        return jsonify({'error': 'Timer not started'})


