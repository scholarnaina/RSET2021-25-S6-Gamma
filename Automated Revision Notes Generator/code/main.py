from flask import Flask, request, render_template, redirect, url_for, flash, send_file, session
import os
from fpdf import FPDF
import io
from bs4 import BeautifulSoup
from summarygen import summarizer 
from werkzeug.utils import secure_filename
import pandas as pd
import unidecode
import re
from nltk.stem import WordNetLemmatizer
import google.generativeai as genai
import fitz

app = Flask(__name__)
app.secret_key = "enter_key_here"
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}  # Allowed file extensions

def process_summary(text):
    # Convert newlines to <br> tags
    text = text.replace('\n', '<br>')
    # Convert **text** to <b>text</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    return text

@app.route('/', methods=['GET'])
@app.route("/home")
def home_route():
    return render_template("home.html")

@app.route('/submit', methods=['POST','GET'])
def submit():
    if request.method == 'GET':
        # Render a form template or redirect as needed when just accessing the URL
        return render_template('home.html')

    module_num = request.form.get('module')  # Retrieves the dropdown value
    file = request.files.get('document')  # Retrieves the file
    module = ['01', '02', '03', '04', '05']
    if module_num[-1] in module:
        modnum = int(module_num[-1])
    else:
        modnum = 0

    if not file or file.filename == '':
        flash('No file selected for uploading')
        return redirect(request.url)

    if file and allowed_file(file.filename):  # Check if the file is allowed
        filename = secure_filename(file.filename)
        file.save(os.path.join('static/uploads/', filename))  # Save file to uploads directory
        summary = summarizer('static/uploads/' + filename, modnum)
        session['summary'] = summary  # Store summary in session
        summary = process_summary(summary) 
    else:
        flash('Allowed file types are - pdf')
        return redirect(request.url)

    return render_template('index.html', summary=summary)

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    summary2 = session.get('summary', '')  # Retrieve summary from session
    if not summary2:
        flash('No summary found to generate PDF')
        return redirect(url_for('home_route'))
    summary2=summary2.replace('<br>','\n')
    summary2=summary2.replace('*','')
    pdf = FPDF(format='letter')
    pdf.add_page()
    pdf.set_font("Arial",style='B',  size=18)
    pdf.cell(200, 10, txt="Summary Notes", ln=True, align="C")
    pdf.set_font("Arial", size=15)

    for line in summary2.split('\n'):
        pdf.multi_cell(0, 10, line)

    pdf_output = io.BytesIO()
    pdf_output.write(pdf.output(dest='S').encode('latin1'))
    pdf_output.seek(0)

    return send_file(pdf_output, mimetype='application/pdf', as_attachment=True, download_name='output.pdf')

if __name__ == "__main__":
    app.run(debug=True)
