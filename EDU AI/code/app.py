from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from sec import secret_key
import joblib
from gemini import make_gemini_request  # Import the make_gemini_request function from gemini.py (assuming it exists)
import random
import json
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.secret_key = secret_key
def read_question(filename):
    with open(filename, 'r') as f:
        return json.load(f)
question_files = ["question1.json", "question3.json", "question5.json", "question7.json", "question9.json"]
def get_db_connection():
    conn = sqlite3.connect('users.db')
    return conn
def get_questions():
    questions = []
    for filename in question_files[:4]:
        question_data = read_question(filename)  # Read data using function (if separate files)
        random_question_index = random.randint(0, len(question_data) - 1)  # Pick a random index
        questions.append(question_data[random_question_index])  # Append the randomly chosen question
    question_data = read_question(question_files[4])  # Read entire 5th file data (if separate files)  # This line you want to integrate# Shuffle options for randomness
    remaining_questions=[]
    i=0
    while(i<=10):
        random_question_index = random.randint(0, len(question_data) - 1)
        if random_question_index not in remaining_questions:
            questions.append(question_data[random_question_index])
            remaining_questions.append(random_question_index)
            i+=1 
    return (questions)
@app.route("/")
def welcome():
    return render_template('welcome.html')
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/material",methods=['GET','POST'])
def material():
    if request.method=="GET":
        return render_template("sub.html")
    if request.method == 'POST':
        # Assuming the selected subject is sent in the request data
        selected_subject = request.form.get('selectedSubject')
        #print("selected",selected_subject)
        # Fetch the user's learning style prediction from the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_results WHERE username = ?", (session.get('username'),))
        #print(session.get('username'))
        predict = cursor.fetchone()
        #print("inside material ",predict)
        if predict:
            session['prediction']=predict[1]
        prediction=session.get('prediction')
        #print("prediction",session.get('prediction'))# Assuming prediction is stored as a single value in the database
        # Use the prediction and selected subject to fetch the material URL from the database
        '''conn = get_db_connection()
        cursor = conn.cursor()'''
        cursor.execute("SELECT Url FROM study_materials WHERE subject= ? AND learning_style = ?", (selected_subject, prediction))
        material_url = cursor.fetchone()
        urls=[]
        url=material_url[0].split(',')
        urls.extend(url)
        #print(urls)# Assuming url is stored as a single value in the database
        conn.close()

        # You may want to pass additional data along with the material URL to the frontend
        # For example, a message to display
        #message = f"Refer to this link for better study of {selected_subject}"

        # Returning the material URL and message as JSON response
        return render_template("sub2.html",urls=urls)


@app.route('/profile',methods=['GET','POST'])
def profile():
    if session.get('logged_in'):
        if request.method=='GET':
            conn = get_db_connection()
            cursor = conn.cursor()
            m=session['username']
            cursor.execute("SELECT * FROM users WHERE username = ?", (m,))
            x=cursor.fetchone()
            conn.close()
            return render_template("profile.html",username=session['username'],name=x[1],phone_number=x[3])
@app.route("/insight")
def insight():
    conn = get_db_connection()
    cursor = conn.cursor()
    username = session.get('username')
    x=session.get("insights")
    #print("username",session.get('username'))
    cursor.execute("SELECT * FROM user_results WHERE username = ?",(username,))
    x=cursor.fetchone()
    #print("isnights",x)
    #print(x)
    conn.close()
    if x:
        session['insights']=x[2]
    x=session.get("insights")
    return render_template("insight.html",insights=x)
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form['Username']
        password = request.form["Password"]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            stored_password = user[2]  # Assuming password is stored at index 2
            if check_password_hash(stored_password, password):
                session["logged_in"] = True
                session["username"] = username        
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM user_results WHERE username = ?", (username,))
                survey_results = cursor.fetchone()
                conn.close()
                if not survey_results:  # Survey results are empty, show survey page
                    return redirect(url_for("survey"))
                else:
                    return redirect(url_for('dashboard'))# Already taken survey, redirect to dashboard
            else:
                error = "Invalid username or password"
        else:
            error = "Invalid username or password"  # Consider more generic message for security
    return render_template("login.html", error=error)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        name = request.form['Name']
        username = request.form['Username']
        password = request.form['Password']
        hashed_password = generate_password_hash(password)
        phono = request.form['Phone_Number']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            error = 'Username already exists'
        else:
            cursor.execute("INSERT INTO users (username, name, password, phone_number) VALUES (?, ?, ?, ?)",(username, name, hashed_password, phono))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
    return render_template('signup.html', error=error)
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('insights',None)
    return redirect(url_for('login'))
@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if session.get('logged_in'):
        if request.method=='GET':
            questions = get_questions()
            return render_template("survey.html",questions=questions)
        if request.method == 'POST':
            clk=joblib.load("mymodel.pkl")
            data = request.get_json()  # This assumes the request sends data as JSON
            answers = []
            a, b, c, d = 0, 0, 0, 0  # Initialize counters
            print("data",data)
            for i, (key, value) in enumerate(data.items()):
                print(i,key,value)
                if i < 4: 
                    print(i)# Handle first four keys
                    if value == '0':
                        print(i)
                        answers.extend([0,1])
                    elif value == '1':
                        print(i)
                        answers.extend([0,1])
                    else:
                        pass
                else:
                    if value == '1':
                        a += 1
                    elif value == '2':
                        b += 1
                    elif value == '3':
                        c += 1
                    elif value == '4':
                        d += 1
                    else:
                        pass
            a=round((a/10)*5)
            b=round((b/10)*5)
            c=round((c/10)*5)
            d=round((d/10)*5)
            answers.extend([a, b, c, d])
            #print([answers])
            predict = clk.predict([answers])  # Call the predict function from model.py
            print("prediction",predict)
            prediction = str(predict)
            prompt = f"Based on the survey results indicating that the person has learning preferences predicted to be {prediction}, generate key insights and recommendations for effective study patterns. Tailor the insights and recommendations to the predicted learning style to enhance comprehension and retention. Provide actionable strategies such as attending lectures regularly, actively participating in discussions, recording lectures for later review, utilizing audio recordings for studying, engaging in study groups, exploring relevant learning tools, incorporating suitable study environments and practices, and seeking appropriate support resources. Ensure that the insights are presented as clear and concise points without additional formatting."
            insights = make_gemini_request(prompt)
            session['insights']=insights
            session['prediction']=prediction
            #print(insights)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_results where username=?",(session['username'],))
            x=cursor.fetchone()
            if x:
                cursor.execute("UPDATE  user_results set prediction=?,insights=? where username=?",(prediction,insights,session['username'],))
                conn.commit()
                conn.close()
                return redirect(url_for('insight'))
            cursor.execute("INSERT INTO user_results (username,prediction, insights) VALUES (?, ?, ?)",(session["username"],prediction, insights))
            conn.commit()
            conn.close()
            return redirect(url_for('insight'))
    else:
        return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True)
