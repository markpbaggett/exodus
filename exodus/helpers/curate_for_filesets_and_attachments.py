import csv


class FileCurator:
    def __init__(self, csv):
        self.original_csv = csv
        self.files_and_attachments = self.__get_files_and_attachments_only()
        self.headers = self.__get_headers()

    def __get_headers(self):
        original_headers = [k for k, v in self.files_and_attachments[0].items()]
        original_headers.append('rdf_type')
        return original_headers

    def __get_files_and_attachments_only(self):
        csv_content = []
        with open(self.original_csv, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['model'] == "Attachment" or row['model'] == "FileSet":
                    csv_content.append(row)
        return csv_content

    def write_files_and_attachments_only(self, filename):
        with open(filename, 'w', newline='') as bulkrax_sheet:
            writer = csv.DictWriter(bulkrax_sheet, fieldnames=self.headers)
            writer.writeheader()
            for data in self.files_and_attachments:
                writer.writerow(data)
        return

    def __write_sheet(self, filename, values, newline=''):
        with open(filename, 'w', newline=newline) as bulkrax_sheet:
            writer = csv.DictWriter(bulkrax_sheet, fieldnames=self.headers)
            writer.writeheader()
            for data in values:
                writer.writerow(data)
        return

    def write_files_and_attachments_only_2(self, base_filename, multi_sheets=False, attachments_per_sheet=500):
        if multi_sheets:
            bundles = [self.files_and_attachments[i:i + attachments_per_sheet] for i in range(0, len(self.files_and_attachments), attachments_per_sheet)]
            for bundle in bundles:
                print(len(bundle))


if __name__ == "__main__":
    x = FileCurator('migrations/arrpgimg_just_filesets_and_attachments.csv')
    x.write_files_and_attachments_only_2('temp/wcc_just_filesets_and_attachments_only.csv', multi_sheets=True)
