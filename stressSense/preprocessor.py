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
