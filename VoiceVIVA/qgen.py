import fitz  # PyMuPDF
import nltk
import spacy
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import random

class QuestionExtractor:
    '''This class contains all the methods required for extracting questions from a given document'''

    def __init__(self, num_questions):
        self.num_questions = num_questions
        self.stop_words = set(stopwords.words('english'))
        self.ner_tagger = spacy.load('en_core_web_md')
        self.vectorizer = TfidfVectorizer()
        self.questions = []

    def get_questions_from_pdf(self, pdf_path):
        '''Returns a list of questions extracted from text in a PDF document'''
        # Open the PDF file
        document = fitz.open(pdf_path)
        text = ""

        # Extract text from each page and concatenate
        for page in document:
            text += page.get_text()

        return self.get_questions(text)

    def get_questions(self, document):
        '''Returns a list of questions extracted from each sentence in the document'''
        sentences = nltk.sent_tokenize(document)  # Tokenize the document into sentences
        for sentence in sentences:
            self._extract_candidate_keywords(sentence)
            self._rank_keywords()
            self._form_questions()  # Modified to add only one question per sentence
        return self.questions

    def _extract_candidate_keywords(self, sentence):
        '''Extracts candidate keywords from the sentence'''
        doc = self.ner_tagger(sentence)
        self.candidate_keywords = []
        for chunk in doc.noun_chunks:
            keyword = chunk.text
            self.candidate_keywords.append(keyword)

    def _rank_keywords(self):
        '''Ranks candidate keywords'''
        self.keyword_scores = {}
        for keyword in self.candidate_keywords:
            score = self._get_keyword_score(keyword)
            self.keyword_scores[keyword] = score
        self.candidate_keywords.sort(key=lambda x: self.keyword_scores[x], reverse=True)

    def _get_keyword_score(self, keyword):
        '''Returns the score for a keyword'''
        score = 0.0
        keyword_tokens = keyword.split()  # Tokenize the keyword
        for token in keyword_tokens:
            score += keyword_tokens.count(token)  # Count occurrences of each token in the keyword
        return score

    def _form_questions(self):
        '''Forms questions from the candidate keywords'''
        if self.candidate_keywords:  # Check if there are candidate keywords
            keyword = self.candidate_keywords[0]  # Take the first keyword as the basis for the question
            random_number = random.randint(1, 3)
            if random_number == 1:
                if keyword.endswith('s'):
                    self.questions.append(f"What are {keyword.lower()}?")
                else:
                    self.questions.append(f"What is {keyword.lower()}?")
            elif random_number == 2:
                self.questions.append(f"Explain {keyword.lower()}.")
            else:
                self.questions.append(f"Define {keyword.lower()}.")

# Instantiate QuestionExtractor with the desired number of questions
num_questions = 20
question_extractor = QuestionExtractor(num_questions)

# Provide the path to your PDF file
pdf_path = "static/DATA STRUCTURES NOTES.pdf"

# Get questions from the PDF document
questions = question_extractor.get_questions_from_pdf(pdf_path)

# # Print the questions
# for idx, question in enumerate(questions, start=1):
#     print(f"{idx}. {question}")
