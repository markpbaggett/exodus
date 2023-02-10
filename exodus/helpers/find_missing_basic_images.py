
def find_works(filename, new_filename):
    works = []
    with open(filename, 'r') as text_file:
        for line in text_file:
            pid = line.replace('info:fedora/', '').replace('\n', '')
            if not pid.startswith('open') and not pid.startswith('restricted') and not pid.startswith('test'):
                works.append(pid)
    with open(new_filename, 'w') as new_text_file:
        for work in works:
            new_text_file.write(f'{work}\n')


if __name__ == "__main__":
    x = "all_basic_images.txt"
    find_works(x, 'basic_images_to_download.txt')
