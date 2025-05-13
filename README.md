# search-query-matching

This script was created to compare a list of search queries to a list of table of contents (TOC) notes.  The intention was to see if user search queries in my library's catalog matched the TOC notes in a group of MARC records.

The script takes two csv files as command line arguments:
1. A list of search queries, with the first item in the row being an identifier and the second item being the text of the search query
2. A list of table of contents notes, again with the first item in the row being an identifier (e.g. MMS ID) and the second item being the TOC

It outpus the results as a csv file, with the search query ID and search string, followed by the identifier of any records whose TOC matched that query.

The script does some basic normalizing of search queries and TOC notes (converting to lowercase and removing punctuation).  It also removes stop words form search queries (using the list of [Primo VE stop words](https://knowledge.exlibrisgroup.com/Primo/Product_Documentation/020Primo_VE/Primo_VE_(English)/160Linguistic_Features_for_Primo_VE#Stop_Words)).
