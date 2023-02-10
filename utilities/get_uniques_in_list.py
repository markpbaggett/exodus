def find_uniques(filename, new_filename):
    uniques = []
    with open(filename, 'r') as text_file:
        for line in text_file:
            pid = line.replace('info:fedora/', '').replace('\n', '')
            if pid not in uniques:
                uniques.append(pid)
    with open(new_filename, 'w') as new_text_file:
        for unique in uniques:
            new_text_file.write(f'{unique}\n')


if __name__ == "__main__":
    x = "all_books_parent_collection.txt"
    find_uniques(x, 'unique_book_collections.txt')