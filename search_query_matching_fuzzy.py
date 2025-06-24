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
from fuzzywuzzy import fuzz


def remove_stop_words(query_string, stop_words):
    """Remove stop words from the list of query_words"""
    query_words = query_string.split()

    new_word_list = []
    for word in query_words:
        if word not in stop_words:
            new_word_list.append(word)

    return " ".join(new_word_list)


def read_csv(filename):
    """Open CSV file and read data into list"""
    data = []
    with open(filename, 'r', encoding='utf-8-sig') as file:
        csv_file = csv.reader(file)
        for row in csv_file:
            data.append(row)
    file.close()
    return data


def main():

    # Define files based on command line input
    query_file = sys.argv[1]
    toc_file = sys.argv[2]
    output_file = os.path.splitext(query_file)[0] + '_results.csv'

    # Get data from TOC and query files
    toc_data = read_csv(toc_file)
    query_data = read_csv(query_file)

    # Open stop_words.txt file and add list of stop words to a list
    with open('stop_words.txt', 'r', encoding='utf-8') as sw_file:
        data = sw_file.read()
        stop_words = data.split('\n')

    # Create list to hold results
    results = []

    # Iterate through each search query
    for query in query_data:
        query_id = query[0]
        query_string = query[1]

        try:
            print(query_id + ' ' + str(query_string))
        except UnicodeEncodeError:
            print('(ENCODING ERROR)')

        # Remove stop words from query word list
        query_normalized = remove_stop_words(query_string, stop_words)

        # Iterate through each table of contents, and see if all words in query are found in that TOC
        for item in toc_data:
            toc_id = item[0]
            toc_string = item[1]

            # Use Token Set Ratio for fuzzywuzzy to evaluate query match to TOC
            fuzzy_ratio = fuzz.token_set_ratio(query_normalized, toc_string, full_process=True)

            # If the fuzzy match is high enough, add record to results list
            # TO-DO: 50 is a somewhat arbitraty limit; evaluate if another number works better
            if fuzzy_ratio > 50:
                print(toc_id)
                print('ratio: ' + str(fuzzy_ratio))

                result = (query_id, query_string, toc_id, fuzzy_ratio)
                results.append(result)

    # Open output file and print results
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        write = csv.writer(f)
        write.writerows(results)
    f.close()

if __name__ == '__main__':
    main()
