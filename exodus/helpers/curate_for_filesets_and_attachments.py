import csv


class FileCurator:
    def __init__(self, csv, curation_type="both"):
        self.original_csv = csv
        self.curation_type = curation_type
        self.files_and_attachments = self.__get_files_and_attachments_only()
        self.headers = self.__get_headers()

    def __get_headers(self):
        original_headers = [k for k, v in self.files_and_attachments[0].items()]
        return original_headers

    def __get_files_and_attachments_only(self):
        csv_content = []
        with open(self.original_csv, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if self.curation_type == "both":
                    if row['model'] == "Attachment" or row['model'] == "FileSet":
                        csv_content.append(row)
                elif self.curation_type == "filesets":
                    if row['model'] == "FileSet":
                        csv_content.append(row)
                elif self.curation_type == "attachments":
                    if row['model'] == "Attachment":
                        csv_content.append(row)
        return csv_content

    def __write_sheet(self, filename, values, newline=''):
        with open(filename, 'w', newline=newline) as bulkrax_sheet:
            writer = csv.DictWriter(bulkrax_sheet, fieldnames=self.headers)
            writer.writeheader()
            for data in values:
                writer.writerow(data)
        return

    def write_files_and_attachments_only(self, base_filename, multi_sheets=False, attachments_per_sheet=500):
        if multi_sheets:
            bundles = [self.files_and_attachments[i:i + attachments_per_sheet] for i in range(0, len(self.files_and_attachments), attachments_per_sheet)]
            i = 0
            for bundle in bundles:
                self.__write_sheet(f"{base_filename.replace('.csv', '')}_{i}.csv", values=bundle)
                i += 1
            return
        else:
            self.__write_sheet(base_filename, values=self.files_and_attachments)
            return


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Add collections to sheet.')
    parser.add_argument("-s", "--sheet", dest="sheet", help="Specify the initial sheet.", required=True)
    parser.add_argument(
        "-f", "--files_sheet", dest="files_sheet", help="Optional: specify files sheet or files sheet pattern."
    )
    parser.add_argument(
        "-m", "--multi_sheets",
        dest="multi_sheets",
        help="multi or single", default="multi"
    )
    parser.add_argument(
        "-t", "--total_size",
        dest="total_size",
        help="If multisheet, the number of attachments and filesets. Must be even.", default=800
    )
    parser.add_argument(
        "-ty", "--type",
        dest="curation_type",
        help="filesets, attachments, both",
        default="both"
    )
    args = parser.parse_args()
    files_sheet = f"{args.sheet.replace('.csv', '')}_with_filesheets_and_attachments_only.csv"
    if args.files_sheet:
        files_sheet = args.files_sheet
    multi_sheet = True
    if args.multi_sheets == "single":
        multi_sheet = False
    x = FileCurator(args.sheet, curation_type=args.curation_type)
    x.write_files_and_attachments_only(
        files_sheet,
        multi_sheets=multi_sheet,
        attachments_per_sheet=int(args.total_size)
    )
