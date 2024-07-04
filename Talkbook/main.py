from flask import Flask, render_template, request, send_file
import os
import joblib
from pydub import AudioSegment
import pyttsx3
import PyPDF2 
app = Flask(__name__)

# Load emotion prediction model
model = joblib.load("emomodel.pkl")

# Function to modulate voice based on emotion
def modulate_voice(emotion_label, text):
    engine = pyttsx3.init()
     # Adjusting voice properties based on emotion label
    if emotion_label == 0:  # Sadness
        engine.setProperty('rate', 100)
        engine.setProperty('volume', 0.5)
        engine.setProperty('pitch', 50)  # Lower pitch for sadness
        engine.setProperty('voice', 'english_rp+f3')  # Choosing a voice for sadness
    elif emotion_label == 1:  # Joy
        engine.setProperty('rate', 200)
        engine.setProperty('volume', 1.0)
        engine.setProperty('pitch', 150)  # Higher pitch for joy
        engine.setProperty('voice', 'english+f5')  # Choosing a voice for joy
    elif emotion_label == 2:  # Love
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.8)
        engine.setProperty('pitch', 100)  # Slightly higher pitch for love
        engine.setProperty('voice', 'english+f2')  # Choosing a voice for love
    elif emotion_label == 3:  # Anger
        engine.setProperty('rate', 180)
        engine.setProperty('volume', 1.0)
        engine.setProperty('pitch', 200)  # Higher pitch for anger
        engine.setProperty('voice', 'english-us')  # Choosing a voice for anger
    elif emotion_label == 4:  # Fear
        engine.setProperty('rate', 160)
        engine.setProperty('volume', 0.7)
        engine.setProperty('pitch', 80)  # Lower pitch for fear
        engine.setProperty('voice', 'english_rp')  # Choosing a voice for fear
    elif emotion_label == 5:  # Surprise
        engine.setProperty('rate', 220)
        engine.setProperty('volume', 1.0)
        engine.setProperty('pitch', 250)  # Higher pitch for surprise
        engine.setProperty('voice', 'english+f4')  # Choosing a voice for surprise
    
    engine.save_to_file(text, 'output.mp3')
    engine.runAndWait()
    output_audio = AudioSegment.from_file("output.mp3")
    return output_audio

# Route for index page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/choose')
def choose():
    return render_template('choose.html')

@app.route('/pdfnew')
def pdfnew():
    return render_template('pdfnew.html')

@app.route('/page2')
def page2():
    return render_template('page2.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/socials')
def socials():
    return render_template('socials.html')

@app.route('/convert', methods=['POST'])
def convert_text_to_audio():
    text = request.json['text']
    text_list = text.split('.')
    gen_audio = AudioSegment.silent(duration=0)
    
    # Modulate voice for each sentence in text
    for line in text_list:
        predicted_emotion = model.predict([line])[0]
        if predicted_emotion==0:
            emotion='Sadness'
        elif predicted_emotion==1:
            emotion='Joy'
        elif predicted_emotion==2:
            emotion=='Love'
        elif predicted_emotion==3:
            emotion='Anger'
        elif predicted_emotion==4:
            emotion='Fear'
        elif predicted_emotion==5:
            emotion='Surprise'
        print(line,'-',emotion)
        output_audio = modulate_voice(predicted_emotion, line)
        gen_audio += output_audio
    
    # Export generated audio
    gen_audio.export("output_audio.mp3", format="mp3")
    
    # Send the audio file to the client
    return send_file("output_audio.mp3", as_attachment=True)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    
    if file.filename == '':
        return "No selected file"
    
    if file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        line=text.split('\n')
        s=''
        for i in line:
            s+=' '
            s+=i
        print(s)
        text_list=s.split('.')
        gen_audio = AudioSegment.silent(duration=0)
    
    # Modulate voice for each sentence in text
        for line in text_list:
            predicted_emotion = model.predict([line])[0]
            if predicted_emotion==0:
                emotion='Sadness'
            elif predicted_emotion==1:
                emotion='Joy'
            elif predicted_emotion==2:
                emotion=='Love'
            elif predicted_emotion==3:
                emotion='Anger'
            elif predicted_emotion==4:
                emotion='Fear'
            elif predicted_emotion==5:
                emotion='Surprise'
            print(line,'-',emotion)
            output_audio = modulate_voice(predicted_emotion, line)
            gen_audio += output_audio
    
    # Export generated audio
        gen_audio.export("output_audio.mp3", format="mp3")
        return send_file("output_audio.mp3", as_attachment=True)

# Run the Flask app
if __name__ == '__main__':
    if os.path.exists("output_audio.mp3"):
        os.remove("output_audio.mp3")  # Remove old audio file if exists
    app.run(debug=True)
