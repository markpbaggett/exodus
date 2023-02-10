import csv
from tqdm import tqdm


class InstitutionOnlyGenerator:
    def __init__(self, original_csv, visibilty):
        self.visibility = visibilty
        self.original_csv = original_csv
        self.original_as_dict = self.__read()
        self.headers = self.__get_headers()
        self.new_csv_with_files = self.__add_new_objects(visibilty)

    def __read(self):
        csv_content = []
        with open(self.original_csv, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                csv_content.append(row)
        return csv_content

    def __get_headers(self):
        original_headers = [k for k, v in self.original_as_dict[0].items()]
        original_headers.append('visibility')
        return original_headers

    def __add_new_objects(self, visibility):
        new_csv_content = []
        for row in tqdm(self.original_as_dict):
            current_data = {}
            for k, v in row.items():
                current_data[k] = v
                current_data['visibility'] = visibility
            new_csv_content.append(current_data)
        return new_csv_content

    def write_csv(self, filename):
        with open(filename, 'w', newline='') as bulkrax_sheet:
            writer = csv.DictWriter(bulkrax_sheet, fieldnames=self.headers)
            writer.writeheader()
            for data in self.new_csv_with_files:
                writer.writerow(data)
        return


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Switch visibility of all items to institution only.')
    parser.add_argument("-s", "--sheet", dest="sheet", help="Specify original csv.", required=True)
    parser.add_argument(
        "-o", "--output_sheet", dest="output_sheet", help="Specify output sheet.", required=True
    )
    parser.add_argument(
        "-v", "--visibility", dest="visibility", help="Specify visibility.", required=True,
        choices=['open', 'restricted', 'authenticated']
    )
    args = parser.parse_args()
    x = InstitutionOnlyGenerator(args.sheet, args.visibility)
    x.write_csv(args.output_sheet)
