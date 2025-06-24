# -*- coding: utf-8 -*-
"""
Uses Primo API to make queries and compare results to a list of MMS IDs, to
identify if those records are in the query search results. Then, if the record
is found, analyzes the PNX display fields to identify which fields match the
query terms.

Created on Tues Jun 3 2025

@author: Elliot Williams
"""

import csv
import sys
import os
import requests
from fuzzywuzzy import fuzz
from credentials import API_KEY

# Set base url for the Primo API
BASE_URL = 'https://api-na.hosted.exlibrisgroup.com/'


def read_csv(filename):
    """Open CSV file and read data into list"""
    data = []
    with open(filename, 'r', encoding='utf-8-sig') as file:
        csv_file = csv.reader(file)
        for row in csv_file:
            data.append(row)
    file.close()
    return data


def primo_search_call(query_string, query_tab, query_vid):
    """"Execute query using the Primo Search API"""

    # Get scope based on tab value
    if query_tab == 'Everything':
        query_scope = 'MyInst_and_CI'
    elif query_tab == 'LibraryCatalog':
        query_scope = 'MyInstitution'
    elif query_tab == 'SpecCol':
        query_scope = 'SpecCol'
    elif query_tab == 'CourseReserves':
        query_scope = 'CourseReserves'
    # If tab does not match any of those values, quit this function and do not make an API call
    else:
        return

    # Set API URL and parameters
    primo_api = BASE_URL + 'primo/v1/search'
    query_params = {
        'vid': query_vid,
        'tab': query_tab,
        'scope': query_scope,
        # In query string, add space after commas
        'q': 'any,contains,' + query_string.replace(',', ', '),
        'multiFacets':
            'facet_rtype,exclude,newspaper_articles|,|facet_rtype,exclude,reviews',
        'pcAvailability': 'false',
        'lang': 'eng',
        'offset': '0',
        'limit': '50',
        'sort': 'rank',
        'getMore': '0',
        'conVoc': 'true',
        'inst': '01UTXSANT_INST',
        'skipDelivery': 'true',
        'disableSplitFacets': 'false',
        'apikey': API_KEY}

    # Make API call
    try:
        response = requests.get(primo_api, params=query_params, timeout=45)
        response.raise_for_status()
    except requests.exceptions.ReadTimeout:
        print('Request timed out.')
        return

    # print(response.url)

    # Return API response formatted as JSON
    return response.json()


def pnx_field_match(item, query_string):
    """Parses API response to get PNX display fields, and does fuzzy matching to see
    which of those fields match the query terms."""

    # Set empty list to hold matching pnx field names
    matching_fields = []

    # Parse JSON to get PNX display fields
    display_fields = item['pnx']['display']

    for field, value in display_fields.items():
        for v in value:
            # Use Token Set Ratio for fuzzywuzzy to evaluate query match to pnx field
            fuzzy_ratio = fuzz.token_set_ratio(query_string, v)

            # If the fuzzy match is high enough, add field name to matching_fields list
            # TO-DO: 50 is a somewhat arbitraty limit; evaluate if another number works better
            if fuzzy_ratio > 50:
                matching_fields.append(field)
                print(field + ' (ratio: ' + str(fuzzy_ratio) + ')')

    return matching_fields


def main():
    """Main function: opens files, gets data, makes API queries, and returns results."""

    # Define files based on command line input
    query_file = sys.argv[1]
    mmsid_file = sys.argv[2]
    output_file = os.path.splitext(query_file)[0] + '_search_matches.csv'

    # Get data from TOC and query files
    mmsid_data = read_csv(mmsid_file)
    query_data = read_csv(query_file)

    # Convert MMS IDs from lists to strings
    mms_ids = []
    for i in mmsid_data:
        mms_id = i[0]
        mms_ids.append(mms_id)

    results = []

    # Loop through queries to make API call and extract MMS IDs of results
    for query in query_data:
        query_id = query[0]
        query_string = query[1]
        query_tab = query[2]
        query_vid = query[3]
        try:
            print(query_id + ' - ' + query_string)
        except UnicodeEncodeError:
            print(query_id + ' - ' + str(query_string.encode("UTF-8")))

        # Send query information to API call and get back results
        primo_response = primo_search_call(query_string, query_tab, query_vid)

        # If no response from API call, move to next query
        if primo_response is None:
            continue

        # Count the total number of results from the API;
        # helpful for confirming that API works as expected
        api_results_count = primo_response['info']['total']
        print(api_results_count)

        # Loop through items in query response
        for item in primo_response['docs']:
            # Get MMS ID from item, if it exists; if not, skip this item
            try:
                item_mms = item['pnx']['display']['mms'][0]
            except KeyError:
                continue

            # Check if item MMS ID is in list of MMS IDs of interest
            if item_mms in mms_ids:
                print('Found! ' + item_mms)

                matching_fields = pnx_field_match(item, query_string)

                # Combine query id, string, and item MMS ID and add to results
                result = [query_id, query_string, item_mms, matching_fields]
                results.append(result)

    # Open output file and print results
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        write = csv.writer(f)
        write.writerows(results)

    f.close()


if __name__ == '__main__':
    main()
