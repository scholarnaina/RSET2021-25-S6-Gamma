import torch
from scipy.spatial.distance import cosine
from transformers import BertTokenizer, BertModel
from nltk.corpus import wordnet

def has_negation(sentence):
    negation_words = ['not', 'no', 'never','non', 'none', 'nobody', 'nothing', 'nowhere']
    tokens = sentence.lower().split()
    for word in negation_words:
        if word in tokens:
            return True
    return False

def has_antonym(sentence1, sentence2):
    antonyms = [('upper', 'lower'), ('higher', 'lower'), ('larger', 'smaller'), ('most', 'least'), ('largest','smallest'), 
                ('highest','lowest'),('adds','removes'),('adds','removing'), ('adds','remove'),
                ('top','bottom'),('rear','front'),('back','front'),('last in','first in'),('lifo','fifo'),
                ('lifo','first in'),('fifo','last in'),('minimum','maximum')]  # Add more antonym pairs as needed

    def get_phrases(sentence):
        phrases = []
        words = sentence.lower().split()
        for i in range(len(words)):
            for j in range(i + 1, len(words) + 1):
                phrases.append(' '.join(words[i:j]))
        return set(phrases)

    phrases1 = get_phrases(sentence1)
    phrases2 = get_phrases(sentence2)

    for phrase1 in phrases1:
        for phrase2 in phrases2:
            if (phrase1, phrase2) in antonyms or (phrase2, phrase1) in antonyms:
                return True
    return False

def cosine_similarity(sentence1, sentence2):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased')

    tokens1 = tokenizer(sentence1, return_tensors='pt', max_length=128, truncation=True, padding=True)
    tokens2 = tokenizer(sentence2, return_tensors='pt', max_length=128, truncation=True, padding=True)

    with torch.no_grad():
        outputs1 = model(**tokens1)

    embeddings1 = outputs1.last_hidden_state.mean(dim=1).squeeze().numpy()

    with torch.no_grad():
        outputs2 = model(**tokens2)

    embeddings2 = outputs2.last_hidden_state.mean(dim=1).squeeze().numpy()

    similarity_score = 1 - cosine(embeddings1, embeddings2)

    # Consider negation
    has_negation_sentence1 = has_negation(sentence1)
    has_negation_sentence2 = has_negation(sentence2)

    # If negation exists in either sentence, invert the similarity score
    if has_negation_sentence1 or has_negation_sentence2:
        if has_negation_sentence1 == has_negation_sentence2:
            similarity_score = similarity_score
        else:    
            similarity_score = 0

    # Consider antonyms
    if has_antonym(sentence1, sentence2):
        similarity_score = 0

    return similarity_score * 5


