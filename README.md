# Search query matching for Primo search results & tables of contents

This repository contains two scripts that were developed to assist with comparing Primo search queries to a set of MARC records. The original goal was to evaluate whether a group of recently-updated records were appearing in search results for top searches in Primo, and if so, what parts of those records matched the search terms.

The first script compares a given list of records against actual Primo search results, using the Primo Search API. The second script compares an output of MARC data (or other data) against a list of search queries to approximate whether those queries would match records with that data.

They were designed to work with the output of the [Popular Searches subject area](https://knowledge.exlibrisgroup.com/Primo/Product_Documentation/020Primo_VE/Primo_VE_(English)/140Primo_VE_Analytics/040Analytics_Subject_Areas_for_Primo_VE#Popular_Searches) in Primo VE Analytics.  

## primo_pnx_matching

This script was created to see if a list of MMS IDs show up in the top results for a search in Primo, and if so, where in the record the search terms are found.

The script uses the [Primo Search API](https://developers.exlibrisgroup.com/primo/apis/search/) to make queries. It is currently configured to match the [UTSA Primo interface](https://utsa.primo.exlibrisgroup.com/discovery/search?tab=LibraryCatalog&search_scope=MyInstitution&vid=01UTXSANT_INST:DEFAULT&facet=rtype,exclude,reviews,lk&facet=rtype,exclude,newspaper_articles,lk), including default filters and available tabs. It then compares the top 50 search results to a list of MMS IDs, to identify if those records are in the query search results. 

Then, if the record is found, it analyzes the PNX display fields to identify which fields match the query terms. (PNX search fields would yield more accurate information, but are not available through the Primo search API.) It uses the [fuzzywuzzy](https://pypi.org/project/fuzzywuzzy/) library's token_set_ratio method to compare the search terms to each PNX field; if the ratio value is greater than 50, that field is returned as a potential match.

Expects two command line arguments:
1. Search query file - CSV file with the following entries: query ID, query string, Primo tab, Primo view
       E.g. "search5,psychology,LibraryCatalog,01UTXSANT_INST:DEFAULT"
2. MMS ID file - CSV file with one MMS ID per line

Output filename is based on the query file name, with "_search_matches" appended. The output is formatted as a CSV file with the following entries: query ID, query string, MMS ID of matching record, list of PNX field names
    
This script requires a credentials.py file with a Primo API key.

## search_query_matching_fuzzy

This script was created to compare a list of search queries to a list of table of contents (TOC) notes.  The intention was to see if user search queries in my library's catalog matched the TOC notes in a group of MARC records.

It also uses the [fuzzywuzzy](https://pypi.org/project/fuzzywuzzy/) library's token_set_ratio method to compare the query terms to the table of contents data. It also removes stop words form search queries (using the list of [Primo VE stop words](https://knowledge.exlibrisgroup.com/Primo/Product_Documentation/020Primo_VE/Primo_VE_(English)/160Linguistic_Features_for_Primo_VE#Stop_Words)).

The script takes two csv files as command line arguments:
1. Search query file - CSV file, with the first item in the row being an identifier and the second item being the text of the search query
2. Table of Contents file - CSV file, with the first item in the row being an identifier (e.g. MMS ID) and the second item being the text of the TOC

The output filename is based on the query file name, with "_results" appended.  The output is formatted as a CSV file, with the search query ID and search string, followed by the identifier of any records whose TOC matched that query. (Each matching record is on its own line.)

The script was designed with table of contents notes in mind, but could also be used for other types of data you want to compare a list of search terms to.
