"""Compares a list of search queries to a list of table of contents (TOC) notes.

Accepts two CSV files as command line arguments: 1) A list of search queries, with the first
item in the row being an identifier and the second item being the text of the search query, and
2) A list of table of contents notes, again with the first item in the row being an identifier
(e.g. MMS ID) and the second item being the TOC. Output is a CSV file, with the search query ID
and search string, followed by the identifier of any records whose TOC matched that query.
"""

import sys
import os
import csv
import string


def normalize_string(text_string):
    """Normalize text to lowercase and remove punctuation"""
    text_string = text_string.lower()
    for x in string.punctuation:
        text_string = text_string.replace(x, ' ')
    return text_string


def remove_stop_words(word_list, stop_words):
    """Remove stop words from the list of query_words"""
    new_word_list = []
    for word in word_list:
        if word not in stop_words:
            new_word_list.append(word)

    return new_word_list


def read_csv(filename):
    """Open CSV file and read data into list"""
    data = []
    with open(filename, 'r', encoding='utf-8-sig') as file:
        csv_file = csv.reader(file)
        for row in csv_file:
            data.append(row)
    file.close()
    return data


def match_terms(query_words, toc):
    """Check to see if all words in query_words are found in the table of contents"""
    return bool(all(x in toc for x in query_words))


def main():

    # Define files based on command line input
    query_file = sys.argv[1]
    toc_file = sys.argv[2]
    output_file = os.path.splitext(query_file)[0] + '_results.csv'

    # Open stop_words.txt file and add list of stop words to a list
    with open('stop_words.txt', 'r') as sw_file:
        data = sw_file.read()
        stop_words = data.split('\n')

    # Get data from TOC and query files
    toc_data = read_csv(toc_file)
    query_data = read_csv(query_file)

    # Normalize the text in the table of contents
    for item in toc_data:
        item[1] = normalize_string(item[1])

    # Create list to hold results
    results = []

    # Iterate through each search query
    for query in query_data:
        query_id = query[0]
        query_string = query[1]

        # Normalize query strings and split into individual words
        query_normalized = normalize_string(query_string)
        query_words = query_normalized.split()

        # Remove stop words from query word list
        query_words = remove_stop_words(query_words, stop_words)
        
        try:
            print(query_id + ' ' + str(query_words))
        except UnicodeEncodeError:
            print('(ENCODING ERROR)')

        # Iterate through each table of contents, and see if all words in query are found in that TOC
        for item in toc_data:
            toc_id = item[0]
            toc_content = item[1]
            terms_found = match_terms(query_words, toc_content)
            if terms_found:
                result = (query_id, query_string, toc_id)
                print(toc_id)
                results.append(result)
    
    # Open output file and print results
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in results:
            query_id = item[0]
            query_string = item[1]
            toc_id = item[2]

            # Print subject code and count, separated by a tab
            f.write(query_id + ',' + query_string + ',' + toc_id + '\n')
            print(query_id + ',' + query_string + ',' + toc_id)
    f.close()

if __name__ == '__main__':
    main()
