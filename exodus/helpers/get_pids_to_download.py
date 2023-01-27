import csv

class PidFinder:
    def __init__(self, original_csv):
        self.original_csv = original_csv
        self.pids_to_download = self.__read()

    def __read(self):
        pids_to_download = []
        with open(self.original_csv, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if '_OBJ_fileset' in row['source_identifier']:
                    pids_to_download.append(row['source_identifier'].replace('_OBJ_fileset', ''))
        return pids_to_download

    def write(self, output_file):
        with open(output_file, 'w') as pids_to_download:
            for pid in self.pids_to_download:
                pids_to_download.write(f"{pid}\n")
        return


if __name__ == "__main__":
    x = PidFinder('archivision_cleanup/archivision_institution_only_filesheets_and_attachments_5.csv')
    x.write('archivision_5.txt')
