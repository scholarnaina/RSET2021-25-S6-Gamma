# S6 Mini Project of RSET 2021-25 Gamma Batch

This project is done by the students of S6 CSE gamma. Edu-AI is a personalized learning app that helps users gain insights and access tailored materials suited to their learning style, which is predicted based on a survey taken during the first login. Users can access materials based on the selected course name tailored to their predicted learning style ,can view their insights and also can retake the survey as per their wish.
**Languages Used:** HTML, CSS, FLASK (Python)

A Random Forest classifier is used for the prediction of learning style.


## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Prerequisites](#prerequisites)
- [Acknowledgements](#acknowledgements)

## Installation
Please follow the below instructions for running the app.

### Prerequisites

- Python 3.x
- pip (Python package installer)

### Steps

1. Clone the repository

```bash
git clone https://github.com/yourusername/EDU-AI.git
```

2. Navigate into the project directory

```bash
cd EDU-AI
```

3. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

4. Install dependencies

```bash
pip install -r requirements.txt
```

5. Set up the API key

   - Create a `.env` file in the project root directory.
   - Add your API key to the `.env` file:

   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

6. Ensure `gemini.py` imports the API key correctly. Here’s an example of how to import the key in `gemini.py`:

   ```python
   import os
   from dotenv import load_dotenv

   load_dotenv()

   GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

   # Use the API key in your functions
   ```

## Usage

How to use the project after installation.

1. Start the Flask server

```bash
python app.py
```

2. Open your web browser and go to `http://127.0.0.1:5000/` to access the app.



## Acknowledgements

Thank to all those who have supported us during our project development.

- [Contributor 1](https://github.com/tojonoy)
- [Contributor 1](https://github.com/thomas0035)
- [Contributor 1](https://github.com/theresejoe)
- [Contributor 1](https://github.com/sairasunny)

```

