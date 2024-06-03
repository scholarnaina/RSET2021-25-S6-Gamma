import re
import nltk
from nltk.corpus import stopwords
import cosineSimilarity


################################################
# KEYWORD GENERATION AND CHECKING
################################################

def find_matched_keywords(answer, keyword_list):
    matched_keywords = []
    for keyword in keyword_list:
        # Add both singular and plural forms of the keyword to the regex pattern
        pattern = r'\b{}s?\b'.format(keyword.lower())
        if re.search(pattern, answer.lower()):
            matched_keywords.append(keyword)
    return matched_keywords

def remove_matched_keywords(answer, matched_keywords):
    for keyword in matched_keywords:
        answer = re.sub(r'\b{}\b'.format(keyword.lower()), '', answer, flags=re.IGNORECASE)
    return answer.strip()

def remove_stopwords(text):
    stop_words = set(stopwords.words('english'))
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return ' '.join(filtered_words)

def compare_user_answer_with_keywords(user_answer, matched_keywords):
    matched_keywords_in_user_answer = []
    user_answer_lower = user_answer.lower()  # Convert user answer to lowercase
    for keyword in matched_keywords:
        if re.search(r'\b{}\b'.format(keyword.lower()), user_answer_lower):  # Convert keyword to lowercase before searching
            matched_keywords_in_user_answer.append(keyword)
    return matched_keywords_in_user_answer

def find_matching_keywords(list1, list2):
    # Convert both lists to sets for efficient intersection operation
    set1 = set(list1)
    set2 = set(list2)
    
    # Find the intersection of the two sets to get the common keywords
    common_keywords = set1.intersection(set2)
    
    return common_keywords

def process_answers(answer, user_answer):
    # List of keywords
    keyword_list = [
        "Stack", "Queue", "Linked List", "Array", "Tree", "Graph", "Heap", "Hash Table", "Binary Search Tree","AVL Tree", "Red-Black Tree", "Trie", "Priority Queue", "Deque", "Circular Queue", "Doubly Linked List","Singly Linked List", "Hash Map", "Upper Bound", "Binary Heap", "Radix Tree", "Skip List", "Splay Tree", "Fenwick Tree","Segment Tree","Push", "Pop", "Last in first out", "First in first out", "FIFO", "LIFO", "Enqueue", "Dequeue", "Insert","Delete", "Search", "Traverse", "Access", "Add Vertex", "Add Edge", "Remove Vertex","Remove Edge", "Depth First Search", "Breadth First Search","DFS","BFS" "Extract Maximum/Minimum","Heapify", "Merge Heaps", "Rotations", "Balancing", "Re-coloring", "Prefix Search","Circular increment/decrement pointers", "upper bound", "lower bound", "time complexity", "space complexity", "Range Sum Query", "Point Update", "Range Query","Spanning Tree", "Minimum Spanning Tree (MST)", "Maximum Spanning Tree", "Graph Representation","Adjacency Matrix", "Adjacency List", "Adjacency Set", "Hash Function", "Collision Resolution","Linear Probing", "Quadratic Probing", "Chaining", "Open Addressing", "B-tree", "B+ Tree", "R-tree","AVL Tree Rotation", "Graph Cycle", "Dijkstra's Algorithm", "Fibonacci Heap", "Disjoint Set", "Bloom Filter","Cartesian Tree", "Suffix Array", "Suffix Tree", "Rope", "Ternary Search Tree", "Multiway Tree","K-d Tree (K-dimensional Tree)", "Quadtree", "Octree", "R-way Trie", "Van Emde Boas Tree", "Patricia Trie","Judy Array", "Multi-dimensional Array", "Circular Buffer", "Radix Heap", "X-fast Trie", "Y-fast Trie","Radix-Patricia Trie", "Link/Cut Tree", "Range Tree", "Wavelet Tree", "Scapegoat Tree", "T-tree","Tangle Tree", "Rope Tree", "Ctrie", "Dancing Links", "Huffman Coding", "Miller-Rabin Primality Test","Tarjan's Algorithm", "Floyd-Warshall Algorithm", "Bellman-Ford Algorithm", "Johnson's Algorithm","Ford-Fulkerson Algorithm", "Dinic's Algorithm", "Edmonds-Karp Algorithm", "Aho-Corasick Algorithm","Z Algorithm", "Persistent Data Structure","efficient", "organization", "storage", "data", "both", "retirement", "design" , "implementation" , "operation" ,"maintenance" , "replacement", "time" ,"memory", "maximum", "average case", "tight bounds", "minimum", "space", "step by step", "solve", "input", "output", "memory", "upper bound", "lower bound", "organize", "store", "contiguous", "zero", "0", "sort", "adjacent", "tree", "parent node", "child", "divide", "conquer", "sorting","search", "linear", "runtime", "element", "next", "previous", "last", "first", "push", "pop", "top", "rear", "back","front", "priority", "heirarchical", "nodes", "edges", "root", "graph", "tranversal", "keys","hash", "map", "hash", "uniform distribution"
    ]

    answer = answer.replace("'","")
    answer = answer.replace(",","")

    # Find matched keywords
    keywords_generated = find_matched_keywords(answer, keyword_list)
    keywords_generated_set = set(keywords_generated)
    keywords_generated = list(keywords_generated_set)

    keywords_user_answer = find_matched_keywords(user_answer,keyword_list)
    keywords_user_set = set(keywords_user_answer)
    keywords_user_answer = list(keywords_user_set)
    
    # Call the function to compare user_answer with matched_keywords
    # matched_keywords_in_user_answer = compare_user_answer_with_keywords(user_answer, keywords_generated)
    matched_keywords_in_user_answer = find_matching_keywords(keywords_generated,keywords_user_answer)

    # Print matched keywords
    if keywords_generated:
        print("Keywords Generated:")
        for keyword in keywords_generated:
            print("-", keyword)
        p = 2    
    else:
        print("No keywords generated.")
        p = 1

    # Print the matched keywords in the user_answer
    if matched_keywords_in_user_answer:
        print("Matched keywords in user answer:")
        for keyword in matched_keywords_in_user_answer:
            print("-", keyword)
    else:
        print("No keywords matched in user answer.")    
        
    # Calculate the percentage of matched keywords in user's answer
    if keywords_generated:
        keyword_score = (len(matched_keywords_in_user_answer) / len(keywords_generated))*5
        print("Keyword Score: {:.1f}".format(keyword_score))
    else:
        print("No keywords to compare.")
        keyword_score = 0


    # Remove matched keywords from the answer
    cleaned_answer = remove_matched_keywords(answer, keywords_generated)

    # Remove stopwords from cleaned answer
    answer2 = remove_stopwords(cleaned_answer)

    cleaned_user_answer = remove_matched_keywords(user_answer, matched_keywords_in_user_answer)

    # Remove stopwords from cleaned answer
    user_answer2 = remove_stopwords(cleaned_user_answer)

    # Print cleaned answer
    print("\nCleaned answer:")
    print(answer2)
    # Print cleaned user answer
    print("\nCleaned user answer:")
    print(user_answer2)

    overall_score = score_generation(answer2, user_answer2, keyword_score, p, answer, user_answer)
    if(user_answer == "" or user_answer.lower() == "i don't know the answer" or user_answer.lower() == "i don't know"):
        return 0
    else:
        return overall_score



################################################
# SYNONYM AND SIMILAR WORDS CHECKING
################################################

from nltk.corpus import wordnet as wn
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from difflib import SequenceMatcher
from nltk.stem import SnowballStemmer, WordNetLemmatizer
import nltk
from textblob import Word

# Initialize Snowball stemmer with language parameter (e.g., 'english')
snowball_stemmer = SnowballStemmer('english')

# # Download WordNet if not already downloaded
# nltk.download('wordnet')

# Initialize WordNet Lemmatizer
lemmatizer = WordNetLemmatizer()


def similar(sentence):
    # Tokenize the sentence into words
    words = nltk.word_tokenize(sentence)
    english_words = set(nltk.corpus.words.words())

    result = []

    for word in words:
        # Stem the word using Snowball stemmer
        stemmed_word = snowball_stemmer.stem(word.lower())

        result.append(stemmed_word)

    final = ""
    for words in result:
            word = Word(words)
            result = word.correct()
            final += result
            final += " "
            
    return final
        

# Function to get synonyms of a word using WordNet
def get_synonyms(word):
    synonyms = set()
    for synset in wn.synsets(word):
        for lemma in synset.lemmas():
            synonyms.add(lemma.name())
    return synonyms

# Function to calculate similarity between two strings
def similarity_score(str1, str2):
    return SequenceMatcher(None, str1, str2).ratio()

# Function to preprocess text (tokenization, removal of stopwords, lemmatization)
def preprocess_text(text):
    tokens = word_tokenize(text)
    tokens = [token for token in tokens if token.lower() not in stopwords.words('english')]
    tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens]
    return tokens

def compare_similarity(answer2, similar_words):
    # Preprocess text
    tokens_answer = preprocess_text(answer2)

    if len(tokens_answer)==0:
        return 0
    
    # Count the number of words in answer2 that are also in similar_words
    matching_words_count = sum(1 for word in tokens_answer if word in similar_words)
    
    # Calculate the ratio of matching words to total words in answer2
    similarity_ratio = matching_words_count / len(tokens_answer)*5
    
    return similarity_ratio



def score_generation(answer2, user_answer2, keyword_score, p, answer, user_answer):

    answer2 = similar(answer2)
    user_answer2 = similar(user_answer2)
    # Preprocess text
    tokens_answer = preprocess_text(answer2)
    tokens_user_answer = preprocess_text(user_answer2)
    s1 = set(tokens_answer)
    s2 = set(tokens_user_answer)
    tokens_answer = list(s1)
    tokens_user_answer = list(s2)
    
    # Initialize a list to store words with similarity score >= 0.7 along with their scores
    similar_words_with_scores = []
    
    # Iterate through each word in cleaned answer
    for word1 in tokens_answer:
        # Initialize the highest similarity score for the current word
        highest_similarity = 0
        
        # Iterate through each word in cleaned user answer
        for word2 in tokens_user_answer:
            # Get the synsets for both words
            synsets_word1 = wn.synsets(word1)
            synsets_word2 = wn.synsets(word2)
            
            # Calculate the similarity between synsets
            max_similarity = 0  # Initialize to 0
            if synsets_word1 and synsets_word2:
                max_similarity = max(s1.path_similarity(s2) or 0 for s1 in synsets_word1 for s2 in synsets_word2)
            
            # Update the highest similarity score for the current word
            if max_similarity > highest_similarity:
                highest_similarity = max_similarity
        
        # If the highest similarity score is >= 0.7, store the word and its score
        if highest_similarity >= 0.7:
            similar_words_with_scores.append((word1, highest_similarity))
    
    # Call the function to find similar words and their scores
    similar_words = []

    # The similar words and their scores
    for word, score in similar_words_with_scores:
        # print(f"Word: {word}, Score: {score}")
        similar_words.append(word)
     
    # Calculate the similarity ratio between answer2 and similar_words
    similarity_score = compare_similarity(answer2, similar_words)
    print("\nSimilarity Score:", similarity_score)    
    partial_score =( keyword_score + similarity_score ) / p
    print("Partial Score: ",partial_score)

    ################################################
    # COSINE SIMILARITY
    ################################################

    cosine_similarity = cosineSimilarity.cosine_similarity(answer, user_answer)
    print("Cosine Similarity: ",cosine_similarity)

    overall_score =( partial_score + cosine_similarity ) / 2
    print("Overall Score: ",overall_score)

    return overall_score
     
# # Input answer
# answer =  "the last node points back to the first node , forming a circular structure"
# user_answer = "circular linked list is a type of linked list in which the front element and the rare elements are next to each other"

# # Process the answers
# overall_score = process_answers(answer, user_answer)