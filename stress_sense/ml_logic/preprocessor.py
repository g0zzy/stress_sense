import string
import re

from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer

def cleaning(sentence):
    '''
    basic cleaning of texts. Probably do not needed for DL models
    '''
    # Removing whitespaces
    sentence = sentence.strip()

    # Lowercasing
    sentence = sentence.lower()

    # Removing numbers
    sentence = ''.join(char for char in sentence if not char.isdigit())

    # Removing punctuation
    for punctuation in string.punctuation:
        sentence = sentence.replace(punctuation, '')

    # Tokenizing
    tokenized = word_tokenize(sentence)

    # Lemmatizing
    lemmatizer = WordNetLemmatizer()
    lemmatized = [lemmatizer.lemmatize(word) for word in tokenized]
    cleaned_sentence = " ".join(lemmatized)
    return cleaned_sentence

def strip_urls(text: str) -> str:
    """
    Remove URLs (http, https, www, youtu links) from a string.
    """
    # remove http/https URLs
    text = re.sub(r"http\S+", "", text)
    # remove www.* URLs
    text = re.sub(r"www\.\S+", "", text)
    # remove youtube short links
    text = re.sub(r"youtu\.be\S+", "", text)
    return text.strip()

def decode_label(label: int) -> str:
    """
    Decode a numeric label to its string representation.
    """
    if label == 0:
        return "Anxiety"
    elif label == 1:
        return "Normal"
    else:
        return "Stress"
