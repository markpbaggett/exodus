import csv
import argparse
import os


class Combiner:
    def __init__(self, list_of_sheets):
        self.all_sheets = self.combine(list_of_sheets)
        self.headers = self.__get_headers(self.all_sheets)

    @staticmethod
    def combine(list_of_sheets):
        return [Importer(sheet).original_as_dict for sheet in list_of_sheets]

    @staticmethod
    def __get_headers(list_of_sheets):
        headers = []
        for sheet in list_of_sheets:
            sheet_headers = [k for k, v in sheet[0].items()]
            for header in sheet_headers:
                if header not in headers:
                    headers.append(header)
        return headers

    def write_csv(self, filename):
        with open(filename, 'w', newline='') as bulkrax_sheet:
            writer = csv.DictWriter(bulkrax_sheet, fieldnames=self.headers)
            writer.writeheader()
            new_csv_content = []
            for sheet in self.all_sheets:
                for row in sheet:
                    current_data = {}
                    for k, v in row.items():
                        current_data[k] = v
                    new_csv_content.append(current_data)
            for data in new_csv_content:
                writer.writerow(data)
        return


class Importer:
    def __init__(self, import_sheet):
        self.original_csv = import_sheet
        self.original_as_dict = self.__read(import_sheet)
        self.headers = self.__get_headers(self.original_as_dict)

    @staticmethod
    def __read(original):
        csv_content = []
        with open(original, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                csv_content.append(row)
        return csv_content

    @staticmethod
    def __get_headers(original):
        return [k for k, v in original[0].items()]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Combine Import Sheets')
    parser.add_argument("-d", "--directory", dest="directory", help="Specify directory with import sheets", required=True)
    parser.add_argument(
        "-o", "--output_sheet", dest="output_sheet", help="Specify output sheet.", required=True
    )
    args = parser.parse_args()
    sheets = []
    for path, directories, files in os.walk(args.directory):
        for filename in files:
            sheets.append(f'{path}/{filename}')
    x = Combiner(sheets)
    x.write_csv(args.output_sheet)
