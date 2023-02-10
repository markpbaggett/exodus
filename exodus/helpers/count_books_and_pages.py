import risearch
import argparse
parser = argparse.ArgumentParser(description='Count books and pages.')
parser.add_argument(
    "-c", "--collection", dest="collection", help="Specify collection.", required=True
)
args = parser.parse_args()
x = risearch.ResourceIndexSearch(riformat='JSON').count_books_and_pages_in_collection(args.collection)
print(x)
