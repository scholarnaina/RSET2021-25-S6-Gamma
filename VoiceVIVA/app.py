
# Import necessary libraries
from flask import Flask, render_template, request, jsonify, send_file , redirect, url_for, session
from test import test_bp
from practice import practice_bp
import main
from flask import send_from_directory, render_template
from werkzeug.utils import secure_filename
import os


# Initialize Flask app
app = Flask(__name__)

app.secret_key = 'APP_SECRET_KEY'

# Define a flag to control question generation
generating_question = False

@app.route('/')
def opening():
    email = ""
    message = ""
    return render_template('landing.html',email=email,message=message)

app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploading')
def upload_form():
    filename = request.args.get('filename')
    session['filename'] = filename
    return render_template("uploadPic.html", filename=filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return 'No file part'
    file = request.files['image']
    if file.filename == '':
        return 'No selected file'
    if file and allowed_file(file.filename):
        # Get the filename from query parameter or use a default name
        filename = session.get('filename')
        session.pop('filename', None) 
        # Construct the filename with desired format
        filename_with_extension = f"{filename}.{file.filename.rsplit('.', 1)[1].lower()}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename_with_extension))
        return redirect(url_for('landing')) 

@app.route('/download')
def download_file():
    image_name = request.args.get('imageName')
    if not image_name:
        return 'No image name provided'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
    if not os.path.exists(filepath):
        return 'File not found'
    return send_from_directory(app.config['UPLOAD_FOLDER'], image_name, as_attachment=True)

# @app.route('/index')
# def index():
#     email = session.get('email')
#     return render_template('index1.html', email=email)


@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        if email:
            session['email'] = email  # Store the email in session
            session['message'] = "Registration Successfull!"
            return jsonify({'message': 'Email received and stored in session'})
        else:
            return jsonify({'error': 'Email not provided'})

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        if email:
            session['email'] = email  # Store the email in session
            session['message'] = "Login Successfull!"
            return jsonify({'message': 'Email received and stored in session'})
        else:
            return jsonify({'error': 'Email not provided'})

    
@app.route('/landing')
def landing():
    email = session.get('email')
    message = session.get('message')
    session.pop('message', None) 
    # session.pop('email', None)  # Clear the email from session after retrieving it
    return render_template('landing.html', email=email, message=message)

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('opening')) 

@app.route('/camera')
def camera():
    email = session.get('email')
    session.pop('message', None) 
    return render_template('camera.html', email=email)

@practice_bp.route('/face_detection')
def face_detection():
    name1 = main.face_recognition_func()
    # Return the random question as JSON
    return jsonify({'name1': name1 })



@app.route('/leaderBoard')
def leaderboard():
    email = session.get('email')
    return render_template('leaderBoard.html', email=email)

# Register Blueprints
app.register_blueprint(test_bp)
app.register_blueprint(practice_bp)


if __name__ == "__main__":
    app.run(debug=True)
