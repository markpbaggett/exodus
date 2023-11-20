import csv


class FileSplitter:
    def __init__(self, csv):
        self.original_csv = csv
        self.files_and_attachments = self.__get_files_and_attachments_only()
        self.headers = self.__get_headers()

    def __get_headers(self):
        original_headers = [k for k, v in self.files_and_attachments['preserve'][0].items()]
        return original_headers

    def __get_files_and_attachments_only(self):
        preserve_content = []
        nonpreserve_content = []
        with open(self.original_csv, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if 'OBJ' in row['source_identifier']:
                    preserve_content.append(row)
                else:
                    nonpreserve_content.append(row)
        return {'preserve': preserve_content, 'nonpreserve': nonpreserve_content}

    def __write_sheet(self, filename, values, newline=''):
        with open(filename, 'w', newline=newline) as bulkrax_sheet:
            writer = csv.DictWriter(bulkrax_sheet, fieldnames=self.headers)
            writer.writeheader()
            for data in values:
                writer.writerow(data)
        return

    def write(self):
        self.__write_sheet(f"{self.original_csv.replace('.csv', '')}_preserve.csv", values=self.files_and_attachments['preserve'])
        self.__write_sheet(f"{self.original_csv.replace('.csv', '')}_nonpreserve.csv", values=self.files_and_attachments['nonpreserve'])
        return


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Split CSV into Preservation and Nonpreservation Files.')
    parser.add_argument("-s", "--sheet", dest="sheet", help="Specify the initial sheet.", required=True)
    args = parser.parse_args()
    x = FileSplitter(args.sheet)
    x.write()
