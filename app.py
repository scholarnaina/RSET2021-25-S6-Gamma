from flask import Flask, request, jsonify,send_file
import os
import secrets
from datetime import datetime
import fitz
from unidecode import unidecode
import pandas as pd
import nltk
import math
import shutil
app = Flask(__name__)
from reportlab.pdfgen import canvas
def find_text_below_images(doc):
    captions = []
    for page_num, page in enumerate(doc, start=1):
        image_blocks = [block for block in page.get_text("dict")["blocks"] if block["type"] == 1]  # type 1 for images
        text_blocks = [block for block in page.get_text("dict")["blocks"] if block["type"] == 0]  # type 0 for text

        for img_block in image_blocks:
            # Coordinates of the image block
            _, img_bottom, _, _ = img_block['bbox']
            closest_text = None
            min_distance = float('inf')

            for text_block in text_blocks:
                text_top = text_block['bbox'][1]

                if text_top > img_bottom:  # Ensure text block is below the image block
                    vertical_distance = text_top - img_bottom
                    if vertical_distance < min_distance:  # Find closest text block below the image
                        min_distance = vertical_distance
                        closest_text = text_block

            if closest_text:
                caption = " ".join([span['text'] for line in closest_text['lines'] for span in line['spans']])
                captions.append(caption)
    return captions

def extract_significant_text(doc):
    rows = []
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text('dict')['blocks']
        for block in blocks:
            if block['type'] == 0:
                for line in block['lines']:
                    for span in line['spans']:
                        text = unidecode(span['text'])
                        if text.strip():
                            rows.append({
                                'xmin': span['bbox'][0],
                                'ymin': span['bbox'][1],
                                'xmax': span['bbox'][2],
                                'ymax': span['bbox'][3],
                                'text': text,
                                'is_upper': text.isupper(),
                                'is_bold': "bold" in span['font'].lower(),
                                'span_font': span['font'],
                                'font_size': span['size'],
                                'page_num': page_num
                            })

    df = pd.DataFrame(rows)
    most_common_font_size = df['font_size'].value_counts().idxmax()
    significant_texts = df[(df['is_bold'] == True) & (df['font_size'] > most_common_font_size) | (df['font_size'] > most_common_font_size)]
    return significant_texts

def process_input(input_file_path, output_file_path):
    # Read input text from the file
    with open(input_file_path, 'r') as input_file:
        input_text = input_file.read().strip()

    # Split the input text using commas as separators
    texts = input_text.split(',')

    # Write the texts to the output file, each on a separate line
    with open(output_file_path, 'w') as output_file:
        for text in texts:
           
            output_file.write(text.strip() + '\n')
   
def is_file_empty(file_path):
    # Open the file in read mode
    with open(file_path, 'r') as file:
        # Read the content of the file
        content = file.read()
        # Check if the content is empty
        if not content:
            return True
        else:
            return False

# Example usage:


def write_text_to_pdf(pdf, text, x, y, max_width, font_name="Helvetica", font_size=14):  # Adjusted font size here
    pdf.setFont(font_name, font_size)
   
    # Split text into lines
    lines = text.split('\n')
   
    # Iterate through lines
    for line in lines:
        words = line.split()
        line = ''
        for word in words:
            # Check if adding the word exceeds the width
            if pdf.stringWidth(line + ' ' + word, font_name, font_size) < max_width:
                line += ' ' + word
            else:
                # Write the line to PDF
                pdf.drawString(x, y, line.strip())
                y -= font_size + 4  # Adjust spacing between lines, increased from 2 to 4
                line = word
        # Write the last line to PDF
        pdf.drawString(x, y, line.strip())
        y -= font_size + 4  # Adjust spacing between lines, increased from 2 to 4

    return y  # Return the updated y-coordinate after writing the text

# Function to check for page break and start new page if needed
def check_page_break(pdf, current_y, line_spacing):
    # Adjust threshold based on font size and line spacing
    if current_y - line_spacing < 50:  # Adjust threshold as needed
        pdf.showPage()  # Start a new page
        return 750  # Adjust starting position for new page
    return current_y

def tokenize_sentences(text):
    return nltk.sent_tokenize(text)

# Extract headings and content from a text file
# Extract headings and content from a text file
def extract_headings_and_content(text_file_path):
    headings_and_content = []
    with open(text_file_path, "r") as text_file:
        lines = text_file.readlines()
        i = 0
        while i < len(lines):
            # Check if the current line is a heading
            if lines[i].strip().startswith("heading:"):
                heading = lines[i].strip().replace("heading:", " ")  # Remove "heading:" from the heading
                content = ''
                i += 1  # Move to the next line after the heading
                # Extract content until the next heading or end of file
                while i < len(lines) and not lines[i].strip().startswith("heading:"):
                    content += lines[i]
                    i += 1
                headings_and_content.append((heading, content))
            else:
                i += 1
    return headings_and_content


# Compute TF-IDF vectors for sentences
def compute_tfidf_vectors(sentences):
    # Tokenize words and remove stop words
    stop_words = set(nltk.corpus.stopwords.words('english'))
    word_tokens = [nltk.word_tokenize(sentence.lower()) for sentence in sentences]
    word_tokens = [[word for word in words if word.isalnum() and word not in stop_words] for words in word_tokens]

    # Compute term frequency (TF)
    term_frequency = []
    for tokens in word_tokens:
        tf = {}
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1
        term_frequency.append(tf)

    # Compute document frequency (DF)
    document_frequency = {}
    for tokens in word_tokens:
        unique_tokens = set(tokens)
        for token in unique_tokens:
            document_frequency[token] = document_frequency.get(token, 0) + 1

    # Compute inverse document frequency (IDF)
    total_documents = len(sentences)
    inverse_document_frequency = {token: math.log(total_documents / (1 + df)) for token, df in document_frequency.items()}

    # Compute TF-IDF vectors
    tfidf_vectors = []
    for tf in term_frequency:
        tfidf_vector = {token: tf[token] * inverse_document_frequency[token] for token in tf}
        tfidf_vectors.append(tfidf_vector)

    return tfidf_vectors

# Compute cosine similarity between vectors
def cosine_similarity(vector1, vector2):
    dot_product = sum(vector1[token] * vector2.get(token, 0) for token in vector1)
    magnitude1 = math.sqrt(sum(value ** 2 for value in vector1.values()))
    magnitude2 = math.sqrt(sum(value ** 2 for value in vector2.values()))
    return dot_product / (magnitude1 * magnitude2) if magnitude1 != 0 and magnitude2 != 0 else 0  # Avoid division by zero
def concatenate_content(input_file_path):
    sections = {}
    current_section = None

    with open(input_file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("heading:"):
                current_section = line
                sections.setdefault(current_section, [])
            else:
                try:
                   sections[current_section].append(line)
                except:
                    print("hi")

    concatenated_sections = {}
    current_heading = None
    current_content = []

    for section, content in sections.items():
        if current_heading is None:
            current_heading = section
            current_content.extend(content)
        elif section != current_heading:
            concatenated_sections[current_heading] = ' '.join(current_content)
            current_heading = section
            current_content = content
        else:
            current_content.extend(content)

    # Add the last section
    concatenated_sections[current_heading] = ' '.join(current_content)

    return concatenated_sections


def write_output(concatenated_sections, output_file_path):
    with open(output_file_path, 'w') as outfile:
        for section, content in concatenated_sections.items():
            outfile.write(section + "\n")
            outfile.write(content + "\n\n")

def concatenate_files(file1_path, file2_path, output_file_path):
    # Open the first file for reading
    with open(file1_path, 'r') as file1:
        content1 = file1.read()

    # Open the second file for reading
    with open(file2_path, 'r') as file2:
        content2 = file2.read()

    # Concatenate the content of the two files
    concatenated_content = content1 + '\n' + content2

    # Write the concatenated content to the output file
    with open(output_file_path, 'w') as output_file:
        output_file.write(concatenated_content)

# Example usage:

def extract_content(lines_file1, lines_file2, output_file):
    # Iterate through each line of the first text file
    for line1 in lines_file1:
        # Remove leading/trailing whitespaces and newline characters
        line1 = line1.strip()
       
        # Initialize a flag to indicate content extraction
        extract_content = False
       
        # Initialize an empty string to store the extracted content
        content = ""
       
        # Iterate through each line of the second text file
        for line2 in lines_file2:
            # Remove leading/trailing whitespaces and newline characters
            line2 = line2.strip()
           
            # Check if the line from the first file matches any line in the second file
            if line1 in line2:
                # Set the flag to start content extraction
                extract_content = True
               
            elif extract_content:
                # Check if the current line contains property tags indicating the end of the content
                if "Font Size" in line2:
                    # Stop content extraction
                    extract_content = False
                else:
                    # Append the current line to the extracted content
                    content += line2 + '\n'
       
        # Write the extracted content to the output file if it's not empty
        if content:
            output_file.write("heading:"+line1 + '\n')
            output_file.write(content + '\n\n')

def extract_and_filter_text(pdf_path, output_folder, desired_font_size, desired_bold_tag):
    # Open the PDF file
    doc = fitz.open(pdf_path)

    # Extracting text and its structure
    block_dict = {}
    page_num = 1
    for page in doc:
        file_dict = page.get_text('dict')  # Get the page dictionary
        block_dict[page_num] = file_dict['blocks']  # Store block information
        page_num += 1

    # Processing the extracted text and its structure
    rows = []
    for page_num, blocks in block_dict.items():
        for block in blocks:
            if block['type'] == 0:
                for line in block['lines']:
                    for span in line['spans']:
                        xmin, ymin, xmax, ymax = span['bbox']  # Extract coordinates
                        font_size = span['size']
                        text = unidecode(span['text'])  # Convert Unicode text to ASCII
                        span_font = span['font']
                        is_upper = text.isupper()  # Check if text is uppercase
                        is_bold = "bold" in span_font.lower()  # Check if text is bold
                        if text.strip():  # Check if text is not empty or whitespace
                            rows.append((xmin, ymin, xmax, ymax, text, is_upper, is_bold, span_font, font_size))
    spans = pd.DataFrame(rows, columns=['xmin', 'ymin', 'xmax', 'ymax', 'text', 'is_upper', 'is_bold', 'span_font', 'font_size'])

    # Open a text file for writing the filtered text
    output_file_path = os.path.join(output_folder, os.path.basename(pdf_path).replace('.pdf', '_extracted.txt'))
    with open(output_file_path, "w") as file:
        # Write the filtered text with property tags to the output file
        for index, row in spans.iterrows():
            if row['font_size'] > desired_font_size and (row['is_bold'] == desired_bold_tag or row['font_size'] > desired_font_size):
                file.write(row['text'])
                file.write(" Font Size: " + str(row['font_size']))
                file.write(" Is Bold: " + str(row['is_bold']))
                file.write("\n")
            else:
                file.write(row['text'])
                file.write("\n")

    print("Filtered text with property tags has been written to", output_file_path)

@app.route('/removeinputfile', methods=['DELETE'])
def remove_file1():
    try:
        # Get the filename from the request JSON
        file_name = request.json.get('fileName')

        if file_name is None:
            raise ValueError('No file name provided')

        # Remove the file
        # Assuming the file exists wherever it was supposed to be stored
        # If there's no uploads folder, you can still remove the file if its path is known
        # For demonstration purposes, let's assume the file is in the current directory
        file_path = file_name

        if os.path.exists(file_path):
            os.remove('uploads.pdf')
            return jsonify({'message': f'File {file_name} removed successfully'}), 200
        else:
            return jsonify({'message': f'File {file_name} does not exist'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/removefile', methods=['DELETE'])
def remove_file():
    try:
        # Get the filename from the request JSON
        file_name = request.json.get('fileName')

        if file_name is None:
            raise ValueError('No file name provided')

        # Remove the file from the server's storage
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'message': f'File {file_name} removed successfully'}), 200
        else:
            return jsonify({'message': f'File {file_name} does not exist'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/uploadtext', methods=['POST'])
def upload_text():
    try:
        # Get the text data from the request JSON
        text_data = request.json.get('textData')
       
        if text_data is None:
            raise ValueError('No text data provided')
       
        # Save the text data to a file
        with open('textfield.txt', 'w') as file:
            file.write(text_data)
       
        # Return a success response
        return jsonify({'message': 'Text data uploaded successfully'}), 200
   
    except Exception as e:
        # Handle any errors that occur
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf' not in request.files:
        return 'No PDF file uploaded', 400
    pdf_file = request.files['pdf']
    # Save the PDF file to a desired location
    pdf_file.save('uploads.pdf')
    return 'PDF file uploaded successfully', 200
UPLOAD_FOLDER = 'uploads'  # Specify the folder where you want to save the uploaded PDFs

@app.route('/uploadref', methods=['POST'])
def upload_file1():
    if 'pdf' not in request.files:
        return 'No PDF file uploaded', 400
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
   
    # Get list of uploaded PDF files
    pdf_files = request.files.getlist('pdf')
   
    for pdf_file in pdf_files:
        if pdf_file.filename == '':
            return 'No selected file', 400

        # Generate a unique filename using timestamp and random string
        # timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        # random_str = secrets.token_hex(4)  # Generate a random string of 8 characters
        # filename = f'{timestamp}_{random_str}.pdf'

        # Save the PDF file to the uploads folder
        pdf_file.save(os.path.join(UPLOAD_FOLDER,pdf_file.filename))

    return 'PDF files uploaded successfully', 200

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
 
        # Retrieve data from the request
        data = request.json

        # Save the PDF file temporarily
        # Perform text extraction, processing, and filtering
        # Load your document
        doc_path = r"C:\Users\UNNICHEN\Desktop\pullfromgithub\New folder\smart-gist\uploads.pdf"
        doc = fitz.open(doc_path)

        # Choose the operation based on the content of the PDF
        output_file_path = r"C:\Users\UNNICHEN\Desktop\pullfromgithub\New folder\smart-gist\topics.txt"
        if any(block['type'] == 1 for page in doc for block in page.get_text("dict")["blocks"]):
            captions = find_text_below_images(doc)
            with open(output_file_path, "w", encoding="utf-8") as file:
                for caption in captions:
                    file.write(caption + "\n")
        else:
            significant_texts = extract_significant_text(doc)
            with open(output_file_path, "w", encoding="utf-8") as file:
                for _, row in significant_texts.iterrows():
                    file.write(row['text'] + "\n")

        print(f"Output has been written to {output_file_path}")
        # Integrate provided code after writing the text to the file
        my_path =r"C:\Users\UNNICHEN\Desktop\pullfromgithub\New folder\smart-gist\uploads.pdf" # Change the path to your desired output file
        doc = fitz.open(my_path)

        # Extracting text and its structure
        block_dict = {}
        page_num = 1
        for page in doc:
            file_dict = page.get_text('dict')  # Get the page dictionary
            block_dict[page_num] = file_dict['blocks']  # Store block information
            page_num += 1

        # Processing the extracted text and its structure
        rows = []
        for page_num, blocks in block_dict.items():
            for block in blocks:
                if block['type'] == 0:
                    for line in block['lines']:
                        for span in line['spans']:
                            xmin, ymin, xmax, ymax = span['bbox']  # Extract coordinates
                            font_size = span['size']
                            text = unidecode(span['text'])  # Convert Unicode text to ASCII
                            span_font = span['font']
                            is_upper = text.isupper()  # Check if text is uppercase
                            is_bold = "bold" in span_font.lower()  # Check if text is bold
                            if text.strip():  # Check if text is not empty or whitespace
                                rows.append((xmin, ymin, xmax, ymax, text, is_upper, is_bold, span_font, font_size))

        # Creating DataFrame
        spans = pd.DataFrame(rows, columns=['xmin', 'ymin', 'xmax', 'ymax', 'text', 'is_upper', 'is_bold', 'span_font', 'font_size'])
        desired_font_size = spans['font_size'].value_counts().idxmax()

        # Define the desired font size and bold tag
        # Specify your desired font size
        desired_bold_tag = True   # Specify if you want bold text or not (True/False)

        # Open a text file for writing
        output_file_path = r"C:\Users\UNNICHEN\Desktop\pullfromgithub\New folder\smart-gist\outputinput.txt"
        with open(output_file_path, "w") as file:
            # Display all text along with property tags for filtered text
            for index, row in spans.iterrows():
                if row['font_size'] > desired_font_size and (row['is_bold'] == desired_bold_tag or row['font_size'] > desired_font_size):
                    file.write("heading:" + row['text'])
                    file.write("\n")
                else:
                    file.write(row['text'])
                    file.write("\n")

        print("Filtered text with property tags has been written to", output_file_path)
        desired_font_size =spans['font_size'].value_counts().idxmax()  # Specify your desired font size
        desired_bold_tag = True   # Specify if you want bold text or not (True/False)
        # else:
        #   input_file_path = r"C:\Users\nammu\Desktop\pullfromgithub\smart-gist\textfield.txt"
        #   output_file_path = r"C:\Users\nammu\Desktop\pullfromgithub\smart-gist\topics.txt"
        #   process_input(input_file_path, output_file_path)
        #   print("hello")
        #   print("Output file created:", output_file_path)
         
# Define input and output folder paths
        input_folder = r"C:\Users\UNNICHEN\Desktop\pullfromgithub\New folder\smart-gist\uploads"
        output_folder = r"C:\Users\UNNICHEN\Desktop\pullfromgithub\New folder\smart-gist\output_folder"

# Create the output folder if it does not exist
        if not os.path.exists(output_folder):
              os.makedirs(output_folder)

# Loop through each PDF file in the input folder
        for file_name in os.listdir(input_folder):
              if file_name.endswith(".pdf"):
                 pdf_path = os.path.join(input_folder, file_name)
                 extract_and_filter_text(pdf_path, output_folder, desired_font_size, desired_bold_tag)
        with open(r'C:\Users\UNNICHEN\Desktop\pullfromgithub\New folder\smart-gist\topics.txt', 'r') as file1:
             lines_file1 = file1.readlines()

# Open the output text file for writing the extracted content
        with open(r'C:\Users\UNNICHEN\Desktop\pullfromgithub\New folder\smart-gist\extracted_content.txt', 'w') as output_file:
    # Iterate over each file in the folder
           folder_path = r'C:\Users\UNNICHEN\Desktop\pullfromgithub\New folder\smart-gist\output_folder'
           for file_name in os.listdir(folder_path):
               file_path = os.path.join(folder_path, file_name)
        # Open each file in the folder for reading
               with open(file_path, 'r') as file:
                   lines_file2 = file.readlines()
                   extract_content(lines_file1, lines_file2, output_file)

        print("Extracted content has been written to extracted_content.txt")
        file1_path = r"C:\Users\UNNICHEN\Desktop\pullfromgithub\New folder\smart-gist\outputinput.txt"
        file2_path = r"C:\Users\UNNICHEN\Desktop\pullfromgithub\New folder\smart-gist\extracted_content.txt"
        output_file_path = r"C:\Users\UNNICHEN\Desktop\pullfromgithub\New folder\smart-gist\concatenated_files.txt"

        concatenate_files(file1_path, file2_path, output_file_path)
        input_file_path = r"C:\Users\UNNICHEN\Desktop\pullfromgithub\New folder\smart-gist\concatenated_files.txt"
        output_file_path =r"C:\Users\UNNICHEN\Desktop\pullfromgithub\New folder\smart-gist\inputsummy.txt"

        concatenated_sections = concatenate_content(input_file_path)
        write_output(concatenated_sections, output_file_path)
        print("Concatenated content written to", output_file_path)
       
        # Input text file path
        text_file_path = r"C:\Users\UNNICHEN\Desktop\pullfromgithub\New folder\smart-gist\inputsummy.txt" # Replace with your file path

# Extract headings and content from the text file
        headings_and_content = extract_headings_and_content(text_file_path)

# Initialize variables to keep track of original sentence indices
        sentence_indices = []

# Output file path
        output_file_path = r"C:\Users\UNNICHEN\Desktop\pullfromgithub\New folder\smart-gist\summy.txt"

# Write extracted sentences to the output file
        with open(output_file_path, "w") as output_file:
          for heading, content in headings_and_content:
            output_file.write(f"{heading}\n")

        # Tokenize sentences in the content
            sentences = tokenize_sentences(content)

        # Update sentence_indices with indices of current sentences
            sentence_indices.extend(range(len(sentence_indices), len(sentence_indices) + len(sentences)))

        # Compute TF-IDF vectors for sentences
            tfidf_vectors = compute_tfidf_vectors(sentences)

        # Compute cosine similarity scores for sentences
            similarity_scores = {}
            for i, vector1 in enumerate(tfidf_vectors):
              max_similarity = 0
              most_similar_sentence_index = None
              for j, vector2 in enumerate(tfidf_vectors):
                if i != j:
                    score = cosine_similarity(vector1, vector2)
                    if score > max_similarity:
                        max_similarity = score
                        most_similar_sentence_index = j
              similarity_scores[i] = (most_similar_sentence_index, max_similarity)

        # Select unique sentences with most similarity
            selected_sentences = set()
            for i, (most_similar_sentence_index, max_similarity) in similarity_scores.items():
              if max_similarity is not None and most_similar_sentence_index is not None and (most_similar_sentence_index, i) not in selected_sentences:
                selected_sentences.add((i, most_similar_sentence_index))

        # Sort selected sentences based on original indices
            sorted_selected_sentences = sorted(selected_sentences, key=lambda x: sentence_indices.index(x[0]))

        # Write selected sentences to the output file
            for i, most_similar_sentence_index in sorted_selected_sentences:
              output_file.write(f" {sentences[i]}\n")
           
            output_file.write("\n")  # Add a newline after each heading

        print(f"Extracted sentences written to: {output_file_path}")
        text_file_path = r"C:\Users\UNNICHEN\Desktop\pullfromgithub\New folder\smart-gist\summy.txt"  # Replace with your file path

# Output PDF file path
        output_pdf_path = r"C:\Users\UNNICHEN\Desktop\pullfromgithub\New folder\smart-gist\summary.pdf"  # Replace with your desired path

# Create a PDF document
        pdf = canvas.Canvas(output_pdf_path)
        pdf.setPageSize((1050,792))
# Starting position for text (adjust as needed)
        current_y = 750  # Experiment with starting position
        line_spacing = 16  # Adjust spacing between lines, increased from 12 to 16

# Open the text file for reading
        with open(text_file_path, "r") as text_file:
    # Iterate through each line in the text file
          for line in text_file:
              current_y = check_page_break(pdf, current_y, line_spacing)  # Check for page break
        # Write text to PDF with text wrapping
              current_y = write_text_to_pdf(pdf, line.strip(), 50, current_y, 1050 - 100, font_size=14)  # Adjusted font size here

# Save the PDF document
        pdf.save()

        print(f"Summarized text written to PDF: {output_pdf_path}")
        # Generate PDF using the filtered text data (replace this with your PDF generation logic)
        # For demonstration purposes, we'll just return a dummy response
        pdf_url = 'http://example.com/path/to/generated_pdf.pdf'
        file_path = "path/to/your/file.txt"

# Check if the file exists before attempting to delete it
        if os.path.exists(file_path):
    # Delete the file
           os.remove(file_path)
        # Clean up temporary files
        folder_path = r"C:\Users\UNNICHEN\Desktop\pullfromgithub\New folder\smart-gist\uploads"

# Check if the folder exists before attempting to delete it
        if os.path.exists(folder_path):
    # Delete the folder and all its contents recursively
           shutil.rmtree(folder_path)
        folder_path = r"C:\Users\UNNICHEN\Desktop\pullfromgithub\New folder\smart-gist\output_folder"
        if os.path.exists(folder_path):
    # Delete the folder and all its contents recursively
           shutil.rmtree(folder_path)
        # Return the URL of the generated PDF
        return jsonify({'pdf_url': pdf_url}), 200



@app.route('/download_pdf', methods=['GET'])
def download_pdf():
    # Assuming you have the PDF file stored locally
    pdf_path = r'C:\Users\UNNICHEN\Desktop\pullfromgithub\New folder\smart-gist\summary.pdf'
    return send_file(pdf_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
