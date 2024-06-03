from nltk.corpus import stopwords
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import time
import numpy as np
from transformers import BertForQuestionAnswering, BertTokenizer
import torch
import concurrent.futures

# Initialize BERT model and tokenizer outside the function for efficiency
model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
tokenizer_for_bert = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

def generate_answers_for_questions_parallel(questions, context1, context2):
    """
    Function to generate answers for questions in given contexts in parallel
    """
    answers = [None] * len(questions)

    def generate_answers_for_question(index, question, context1, context2):
        """
        Function to generate answer for a single question in given contexts
        """
        answer1, start_score1, end_score1 = bert_question_answer(question, context1)
        answer2, start_score2, end_score2 = bert_question_answer(question, context2)

        # Choose the answer with higher score
        if start_score1 + end_score1 > start_score2 + end_score2:
            answer = answer1
            start_score = start_score1
            end_score = end_score1
        else:
            answer = answer2
            start_score = start_score2
            end_score = end_score2

        return index, answer, start_score, end_score

    # Use concurrent processing to generate answers
    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
        answer_futures = [executor.submit(generate_answers_for_question, index, question, context1, context2) for index, question in enumerate(questions)]
        for future in concurrent.futures.as_completed(answer_futures):
            try:
                index, answer, start_score, end_score = future.result()
                answers[index] = (answer, start_score, end_score)
            except Exception as e:
                answers[index] = (str(e), 0, 0)

    return answers

def bert_question_answer(question, passage, max_len=512):
    # Tokenize input question and passage
    input_ids = tokenizer_for_bert.encode(question, passage, max_length=max_len, truncation='only_second')

    # Getting number of tokens in 1st sentence (question) and 2nd sentence (passage that contains answer)
    sep_index = input_ids.index(102)
    len_question = sep_index + 1
    len_passage = len(input_ids) - len_question

    # Need to separate question and passage
    # Segment ids will be 0 for question and 1 for passage
    segment_ids = [0] * len_question + [1] * len_passage

    # Converting token ids to tokens
    tokens = tokenizer_for_bert.convert_ids_to_tokens(input_ids)

    # Getting start and end scores for answer
    # Converting input arrays to torch tensors before passing to the model
    start_token_scores = model(torch.tensor([input_ids]), token_type_ids=torch.tensor([segment_ids]))[0]
    end_token_scores = model(torch.tensor([input_ids]), token_type_ids=torch.tensor([segment_ids]))[1]

    # Converting scores tensors to numpy arrays
    start_token_scores = start_token_scores.detach().numpy().flatten()
    end_token_scores = end_token_scores.detach().numpy().flatten()

    # Getting start and end index of answer based on highest scores
    answer_start_index = np.argmax(start_token_scores)
    answer_end_index = np.argmax(end_token_scores)

    # Getting scores for start and end token of the answer
    start_token_score = np.round(start_token_scores[answer_start_index], 2)
    end_token_score = np.round(end_token_scores[answer_end_index], 2)

    # Combining subwords starting with ## and get full words in output.
    # It is because tokenizer breaks words which are not in its vocab.
    answer = tokens[answer_start_index]
    for i in range(answer_start_index + 1, answer_end_index + 1):
        if tokens[i][0:2] == '##':
            answer += tokens[i][2:]
        else:
            answer += ' ' + tokens[i]

    # If the answer didn't find in the passage
    if (start_token_score < 0) or (answer_start_index == 0) or (answer_end_index < answer_start_index) or (
            answer == '[SEP]'):
        answer = "Sorry!, I was unable to discover an answer in the passage."

    return answer, start_token_scores[answer_start_index], end_token_scores[answer_end_index]

def generate_answers(questions):
    # Input contexts
    context1 = """ This is context1. Data-Structures are foundational components in computer science that facilitate the efficient organization, storage, and manipulation of data in various applications and algorithms.
    Data structures are fundamental components that facilitate the efficient organization, storage, and manipulation of data in computer science. 
    The system life cycle is the stages through which the system progresses involving design, implementation, operation, maintenance, and replacement. Linear data structures are data structures in which elements are arranged in a linear sequence 
    Time complexity and space complexity refers to the amount of time an algorithm takes to run and the amount of memory it requires respectively. Time complexity measures the amount of time an algorithm takes to run based on the size of its input, while space complexity measures the amount of memory an algorithm requires as its input size grows. The upper bound or worst case scenario represents the maximum time or space required by an algorithm to run. Time and space complexity are measures that reflects the amount of time and memory required for their execution, respectively.
    Big theta represents tight bounds or average case scenarios in algorithm complexity analysis. The lower bound or best case scenario represents the minimum time or space required by an algorithm to run. An algorithm is a step by step procedure used to solve a problem or perform a task. Algorithm characteristics include input, output, definiteness, finiteness, effectiveness, and generality. Performance analysis evaluates the efficiency and effectiveness of algorithms (in terms of time and space complexity). 
    Big O notation describes the upper bound of an algorithm's time or space complexity, while Big Omega notation represents the lower bound  of an algorithm's time or space complexity. Fundamental data structures are basic structures used to store and organize data effectively. Arrays are linear stuctures where collections of elements are stored in contiguous memory locations. Sparse matrices are matrices where most elements are zero, requiring efficient representations for optimization. Bubble sort comparing adjacent elements and swaps them if they are in the wrong order. 
    A heap-data-structure is a tree based structure where each parent node is greater (or smaller) than its child nodes. Dynamic memory allocation is the process of assigning memory space to a program during runtime, enabling flexible memory management and allocation based on program requirements.
    Depth first search and breadth first search are graph traversal algorithms used to explore and analyze graphs efficiently. Merge sort is a divide and conquer sorting algorithm that recursively divides the array into smaller subarrays, sorts them, and then merges them back together. Search algorithms are used to find elements within data structures. Linear-Search is a searching algorithm which sequentially checks each element until a match is found. Binary-Search divides the array into halves and uses the middle value to eliminate elements in each iteration. Dynamic memory allocation allows programs to allocate memory at runtime.
    End of context1 """
    context2 = """ This is context2.
    Complex data structures are structures composed of multiple simpler data structures, such as singly linked lists, where each element contains a reference to the next element, or doubly linked lists, where each element contains references to both the next and previous elements. Time and space complexity are measures that reflects the amount of time and memory required for their execution respectively. Circular-Linked-Lists are linked lists where the last node points back to the first node, forming a circular structure. A fundamental data structure is a basic structure used to organize and store data efficiently, like stacks. Stacks have have two main operations: push operation adds an element to the top of the stack, and pop operation removes an element from the top of the stack.
    Queue is a linear structure which follows the First In First Out, FIFO principle. Queue has two primary operations: enqueue which adds an element to the rear or back of the queue and dequeue which removes the front element from the queue. Collision resolution refers to methods that handle situations where multiple keys map to the same value in a hash table. Circular Queue is a type of queue data structure in which the last element is connected to the first element, forming a circular arrangement. A priority queue is a type of queue where each element has an associated priority. A double ended queue supports insertion and deletion of elements from both ends. 
    Trees are Hierarchical data structures composed of nodes connected by edges, with root nodes and child nodes. The hashkeys properties include uniqueness, uniform distribution and consistency which are essential for efficient hashing-operations. Stacks are abstract data structures that follow the Last In First Out (LIFO) principle. Hierarchical data structures organize data in a tree like structure with parent and child relationships. Binary Trees are trees where each node has at most two children. Binary Search Trees are binary trees that maintain a specific ordering property, facilitating efficient search operations. Hashing is a technique used to convert keys into indices within a hash table.
    Non linear data structures are data structures that do not organize elements in a sequential manner. Graph is a non linear data structure consisting of vertices (nodes) and edges that represent relationships or connections between those vertices. Sorting algorithms are methods used to rearrange elements in a specified order within a collection, such as arrays, with bubble sort comparing adjacent elements and swapping them if they are in the wrong order.
    Depth first search and breadth first search are graph traversal algorithms used to explore and analyze graphs efficiently. Depth First Search explores as far as possible along each branch before backtracking while Breadth First search explores neighbors of a vertex before moving to the next level.A hash table is a structure that stores key-value pairs allowing for efficient retrieval and storage of data. It achieves this efficiency by using a hashing-function to map keys to indices in an array, where the corresponding values are stored. The hashkeys properties include uniqueness, uniform distribution and consistency which are essential for efficient hashing-operations.
    End of context2."""

    context1 = context1.replace("-", "")
    context2 = context2.replace("-", "")

    # Input questions
    new_questions = []

    for question in questions:
        if question.endswith('s.'):
            question = question.replace("Define", "What are")
            question = question.replace("Explain", "What are")
        else:
            question = question.replace("Define", "What is")
            question = question.replace("Explain", "What is")
        
        if " and " in question:
            question = question.replace("What is", "What are")
            question = question.replace("What are", "What are")
        
        new_questions.append(question)

    # Benchmarking code to measure execution time
    start_time = time.time()
    answers = generate_answers_for_questions_parallel(new_questions, context1, context2)
    end_time = time.time()
    print("Total execution time:", end_time - start_time)
    return {question: answers[i] for i, question in enumerate(questions)}