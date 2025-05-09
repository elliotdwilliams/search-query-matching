import sys
import csv
import re
import string


def normalize_string(text_string):
    """Normalize text to lowercase and remove punctuation"""
    text_string = text_string.lower()
    for x in string.punctuation:
        text_string = text_string.replace(x, ' ')
    return text_string


def remove_stopwords(word_list, stop_words):
    """Remove stop words from the list of query_words"""
    new_word_list = []
    for word in word_list:
        if word not in stop_words:
            new_word_list.append(word)

    return new_word_list


def match_terms(query_words, toc):
    """Check to see if all words in query_words are found in the table of contents"""
    if all(x in toc for x in query_words):
        return True
    else:
        return False


def main():

    # Define files based on command line input
    QUERY_FILE = sys.argv[1]
    TOC_FILE = sys.argv[2]
    
    # Open stop_words.txt file and add list of stop words to a list
    with open('stop_words.txt', 'r') as sw_file:
        data = sw_file.read()
        STOP_WORDS = data.split('\n')

    # Create empty list to hold table of contents data
    toc_data = []

    # Open TOC file and add data to toc_data
    with open(TOC_FILE, 'r') as toc_csv:
        csvFile = csv.reader(toc_csv)
        for row in csvFile:
            toc_data.append(row)
    toc_csv.close()

    # Normalize the text in the table of contents
    for item in toc_data:
        item[1] = normalize_string(item[1])

    # Create empty list to hold query data
    query_data = []

    # Open query file and add data to query_data
    with open(QUERY_FILE, 'r') as query_csv:
        csvFile = csv.reader(query_csv)
        for row in csvFile:
            query_data.append(row)
    query_csv.close()

    # Iterate through each search query
    for query in query_data:
        query_id = query[0]
        query_string = query[1]
        # print(query_string)
        print(query_id)

        # Normalize query strings and split into individual words
        query_string = normalize_string(query_string)
        query_words = query_string.split()

        # Remove stop words from query word list
        query_words = remove_stopwords(query_words, STOP_WORDS)
        print(query_words)

        # Iterate through each table of contents, and see if all words in query are found in that TOC
        for item in toc_data:
            terms_found = match_terms(query_words, item[1])
            if terms_found:
                print(item[0])

            # if all(x in item[1] for x in query_words):
            #     print(item[0])


if __name__ == '__main__':
    main()