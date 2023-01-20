import csv
import tqdm

class ImportReader:
    def __init__(self, csv_file, pattern='archivision_5'):
        self.csv_file = csv_file
        self.pattern = pattern
        self.original_as_dict = self.__read()
        self.headers = self.__get_headers()
        self.objs = self.__get_objs()
        self.new_csv_data = self.__fix_path_to_objects()


    def __get_objs(self):
        csv_content = []
        with open(self.csv_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['model'] == "FileSet" and 'OBJ' in row['title']:
                    csv_content.append(row['remote_files'].split('/')[6])
        return csv_content

    def __read(self):
        csv_content = []
        with open(self.csv_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                csv_content.append(row)
        return csv_content

    def __fix_path_to_objects(self):
        new_csv_content = []
        for row in self.original_as_dict:
            if row['remote_files'] != "" and 'OBJ' in row['title']:
                pid = row['remote_files'].split('/')[6]
                row['remote_files'] = f'https://dlweb.lib.utk.edu/dlwebtemp/{self.pattern}/{pid}.tif'
                new_csv_content.append(row)
            else:
                new_csv_content.append(row)
        return new_csv_content

    def write(self, output_file):
        with open(output_file, 'w') as new_output:
            for obj in self.objs:
                new_output.write(f'{obj}\n')
        return

    def __get_headers(self):
        original_headers = [k for k, v in self.original_as_dict[0].items()]
        return original_headers

    def write_csv(self, filename):
        with open(filename, 'w', newline='') as bulkrax_sheet:
            writer = csv.DictWriter(bulkrax_sheet, fieldnames=self.headers)
            writer.writeheader()
            for data in self.new_csv_data:
                writer.writerow(data)
        return


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Change URLs for Filesets.')
    parser.add_argument("-s", "--sheet", dest="sheet", help="Specify original csv.", required=True)
    parser.add_argument("-p", "--pattern", dest="pattern", help="Specify pattern part.", required=True)
    parser.add_argument(
        "-o", "--output_sheet", dest="output_sheet", help="Specify output sheet.", required=True
    )
    args = parser.parse_args()
    #x = ImportReader('archivision/archivision_institution_only_filesheets_and_attachments_0_restricted.csv')
    x = ImportReader(args.sheet, args.pattern)
    #x.write_csv('archivision_new_cleanup/archivision_institution_only_filesheets_and_attachments_5.csv')
    x.write_csv(args.output_sheet)
