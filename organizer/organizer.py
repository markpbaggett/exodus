import csv


class FileOrganizer:
    def __init__(self, csv):
        self.original_csv = csv
        self.original_as_dict = self.__read()
        self.headers = self.__get_headers()
        self.new_csv_with_files = self.__add_files()

    def __read(self):
        csv_content = []
        with open(self.original_csv, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                csv_content.append(row)
        return csv_content

    def __get_headers(self):
        return [k for k, v in self.original_as_dict[0].items()]

    @staticmethod
    def __add_a_file(filename, row):
        default_headings = ('source_identifier', 'model', 'file', 'title', 'description', 'parents')
        initial_data = {
            'source_identifier': f"{row['source_identifier']}_{filename}",
            'model': "FileSet",
            'file': f"{row['source_identifier'].replace('_', ':')}_{filename}",
            'title': filename,
            'description': f"{filename} for {row['source_identifier']}",
            'parents': row['source_identifier']
        }
        for k, v in row.items():
            if k not in default_headings:
                initial_data[k] = ''
        return initial_data

    def __add_files(self):
        # TODO: Refactor to be agnostic on files
        new_csv_content = []
        for row in self.original_as_dict:
            new_csv_content.append(row)
            new_csv_content.append(self.__add_a_file('PDF', row))
            new_csv_content.append(self.__add_a_file('MODS', row))
        return new_csv_content

    def write_csv(self, filename):
        with open(filename, 'w', newline='') as bulkrax_sheet:
            writer = csv.DictWriter(bulkrax_sheet, fieldnames=self.headers)
            writer.writeheader()
            for data in self.new_csv_with_files:
                writer.writerow(data)
        return


if __name__ == "__main__":
    x = FileOrganizer('temp/samvera_brehm.csv')
    x.write_csv('temp/brehm_with_files.csv')
