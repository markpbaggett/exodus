import csv

class MyCSV:
    def __init__(self, path):
        self.path = path
        self.headers = self.__find_headers()

    def __find_headers(self):
        with open(self.path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            first = next(reader)
            return list(set(key for key in first.keys()))


class ExportCSV:
    def __init__(self, path, new_keys):
        self.path = path
        self.new_keys = new_keys

    def read_and_write_csv(self):
        with open(self.path, 'r', newline='') as infile:
            reader = csv.DictReader(infile)

            # Create list of dictionaries with existing keys plus new keys
            data = []
            for row in reader:
                row.update((key, '') for key in self.new_keys)
                data.append(row)
        with open(self.path, 'w', newline='') as outfile:
            fieldnames = reader.fieldnames + self.new_keys
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)

            # Write header row to CSV file
            writer.writeheader()

            # Write data to CSV file
            writer.writerows(data)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Read a csv and print the headers.')
    parser.add_argument("-s", "--sheet", dest="sheet", help="Specify new csv.", required=True)
    parser.add_argument("-o", "--old_sheet", dest="old_sheet", help="Specify old csv.", required=True)
    args = parser.parse_args()
    new_sheet = MyCSV(args.sheet).headers
    old_sheet = MyCSV(args.old_sheet).headers
    missing_headers = list(set(old_sheet) - set(new_sheet))
    ExportCSV(args.sheet, missing_headers).read_and_write_csv()
