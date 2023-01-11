import csv
import tqdm

class ImportReader:
    def __init__(self, csv_file):
        self.csv_file = csv_file
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
                row['remote_files'] = f'https://dlweb.lib.utk.edu/dlwebtemp/archivision_0/{pid}.tif'
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
    x = ImportReader('archivision/archivision_institution_only_filesheets_and_attachments_0_restricted.csv')
    #x.write('archvision_0.txt')
    x.write_csv('archivision_cleanup/archivision_institution_only_filesheets_and_attachments_0.csv')
