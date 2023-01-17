import csv
import tqdm


class BatchDelete:
    def __init__(self, csv):
        self.csv = csv

    def __read(self):
        csv_content = []
        with open(self.original_csv, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                csv_content.append(row)
        return csv_content

    def __get_headers(self):
        original_headers = [k for k, v in self.original_as_dict[0].items()]
        original_headers.append('delete')
        return original_headers

    def __add_new_objects(self):
        new_csv_content = []
        for row in tqdm(self.original_as_dict):
            current_data = {}
            for k, v in row.items():
                current_data[k] = v
                if row['model'] == 'FileSet':
                    current_data['delete'] = 'TRUE'
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
    parser = argparse.ArgumentParser(description='Batch delete filesets.')
    parser.add_argument("-s", "--sheet", dest="sheet", help="Specify original csv.", required=True)
    parser.add_argument(
        "-o", "--output_sheet", dest="output_sheet", help="Specify output sheet.", required=True
    )
    args = parser.parse_args()
    x = BatchDelete(args.sheet)
    x.write_csv(args.output_sheet)