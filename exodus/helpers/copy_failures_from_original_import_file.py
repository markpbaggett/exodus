import csv


class FailuresFinder:
    def __init__(self, original_csv, failed_imports):
        self.original_csv = original_csv
        self.failures = self.__get_failures_only(original_csv, failed_imports)
        self.headers = self.__get_headers()

    def __get_headers(self):
        original_headers = [k for k, v in self.failures[0].items()]
        return original_headers

    @staticmethod
    def __get_failures_only(original, failures):
        csv_content = []
        failed_to_import = []
        with open(failures, 'r') as failures_file:
            for line in failures_file:
                failed_to_import.append(line.strip())
        with open(original, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['source_identifier'] in failed_to_import:
                    csv_content.append(row)
        return csv_content

    def write_new_import_file_with_failures_only(self, filename, newline=''):
        with open(filename, 'w', newline=newline) as bulkrax_sheet:
            writer = csv.DictWriter(bulkrax_sheet, fieldnames=self.headers)
            writer.writeheader()
            for data in self.failures:
                writer.writerow(data)
        return


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Copy failures data from import sheet.')
    parser.add_argument(
        "-s", "--sheet", dest="sheet", help="Specify the initial sheet.", required=True
    )
    parser.add_argument(
        "-f", "--failures", dest="failures", help="Specify list of files that failed to import."
    )
    args = parser.parse_args()
    x = FailuresFinder(
        args.sheet,
        args.failures
    )
    x.write_new_import_file_with_failures_only(f'failures/{args.sheet.split("/")[-1].replace(".txt", ".csv")}')
