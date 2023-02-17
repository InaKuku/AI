import pandas as pd
import gensim
import re
import nltk
from nltk.tokenize.treebank import TreebankWordDetokenizer


def depure_data(data):
    # Remove new line characters
    data = re.sub('\s+', ' ', data)

    # Remove distracting single quotes
    data = re.sub("\'", "", data)

    return data


def sent_to_words(sentences, minimal_length):
    '''
    Swap capital letters for small ones, remove accents and remove small words
    '''
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True, min_len=minimal_length))


def detokenize(text):
    '''
    Detokenize the given text
    :param text
    :return: detokenized text
    '''
    return TreebankWordDetokenizer().detokenize(text)


def take_conclusion(df):
    '''
    Takes a dataframe, explores the columns "texts" and checks
    for 'conclusion' inside; if present, swaps the abstract for
    the its conclusion part
    :param df: Dataframe
    :return: Texts as list
    '''
    texts_list = df['text'].values.tolist()

    for text_index in range(len(texts_list)):
        text = texts_list[text_index].lower()
        if "conclusion" in text:
            text = text[text.index('conclusion'):]
            texts_list[text_index] = text

    return texts_list






