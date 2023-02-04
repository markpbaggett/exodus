import csv


class WorkChunker:
    def __init__(self, csv):
        self.original_csv = csv
        self.works = self.__get_works()
        self.headers = self.__get_headers()

    def __get_headers(self):
        original_headers = [k for k, v in self.works[0].items()]
        return original_headers

    def __get_works(self):
        csv_content = []
        with open(self.original_csv, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['model'] == "Image" or row['model'] == "Collection":
                    csv_content.append(row)
        return csv_content

    def write_works(self, base_filename, multi_sheets=False, works_per_sheet=500):
        if multi_sheets:
            bundles = [self.works[i:i + works_per_sheet] for i in range(0, len(self.works), works_per_sheet)]
            i = 0
            for bundle in bundles:
                self.__write_sheet(f"{base_filename.replace('.csv', '')}_{i}.csv", values=bundle)
                i += 1
            return
        else:
            self.__write_sheet(base_filename, values=self.works)
            return

    def __write_sheet(self, filename, values, newline=''):
        with open(filename, 'w', newline=newline) as bulkrax_sheet:
            writer = csv.DictWriter(bulkrax_sheet, fieldnames=self.headers)
            writer.writeheader()
            for data in values:
                writer.writerow(data)
        return


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Chunk sheets into sheets.')
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
    args = parser.parse_args()
    files_sheet = f"chunks/{args.sheet.replace('.csv', '')}_chunk.csv"
    if args.files_sheet:
        files_sheet = args.files_sheet
    multi_sheet = True
    if args.multi_sheets == "single":
        multi_sheet = False
    x = WorkChunker(args.sheet)
    x.write_works(
        files_sheet,
        multi_sheets=multi_sheet,
        works_per_sheet=int(args.total_size)
    )
