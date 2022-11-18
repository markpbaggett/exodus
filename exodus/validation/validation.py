import yaml
import csv


class ValidateMigration:
    def __init__(self, profile, migration_sheet):
        self.csv = migration_sheet
        self.loaded_csv = self.__read_csv()
        self.profile = profile
        self.loaded_m3 = yaml.safe_load(open(profile))
        self.all_exceptions = []

    def __read_csv(self):
        csv_content = []
        with open(self.csv, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                csv_content.append(row)
        return csv_content

    def validate_model(self, row):
        models = [k for k, v in self.loaded_m3['classes'].items()]
        if row['model'] != "FileSet" and row['model'] != "Collection":
            if row['model'] not in models:
                self.all_exceptions.append(f'{row["source_identifier"]} has invalid model {row["model"]}.')
        return

    def iterate(self):
        for row in self.loaded_csv:
            self.validate_model(row)
        separator = "\n"
        if len(self.all_exceptions) > 0:
            raise Exception(f"Migration spreadsheet has {len(self.all_exceptions)} problems: {separator.join(self.all_exceptions)}")
        else:
            print("Sheet passes all tests.")


x = ValidateMigration(profile='temp/utk.yml', migration_sheet='temp/gamble_good2_with_collections.csv')
x.iterate()