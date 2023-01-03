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

    def validate_license(self, row):
        if 'license' in row and row['license'] != "":
            if 'http://' not in row['license']:
                self.all_exceptions.append(f'{row["source_identifier"]} has invalid license: {row["license"]}.')

    def validate_values(self, row):
        system_fields = ("source_identifier", "model", "remote_files", "parents", "visibility")
        for k, v in row.items():
            if k not in system_fields and row['model'] != "FileSet" and row['model'] != "Collection":
                review_property = self.check_property(k)
                if review_property:
                    available_on = self.check_available_on(row, k, v)
                    if available_on:
                        self.check_cardinality(row, k, v)
                        self.check_range(k, v, row)
        return

    def check_available_on(self, row, key, value):
        if row['model'] not in self.loaded_m3['properties'][key]['available_on']['class'] and value != "":
            self.all_exceptions.append(f"{key} is not available on {row['model']} for {row['source_identifier']}.")
            return False
        elif row['model'] not in self.loaded_m3['properties'][key]['available_on']['class']:
            return False
        else:
            return True

    def check_property(self, key):
        if key not in self.loaded_m3['properties']:
            self.all_exceptions.append(f"{key} is not listed in the m3 profile.")
            return False
        else:
            return True

    def check_cardinality(self, row, key, value):
        maximum = self.loaded_m3['properties'][key]['cardinality']['maximum'] if 'maximum' in self.loaded_m3['properties'][key]['cardinality'] else 1000
        minimum = self.loaded_m3['properties'][key]['cardinality']['minimum'] if 'minimum' in self.loaded_m3['properties'][key]['cardinality'] else 0
        all_values = [thing for thing in value.split(' | ') if thing != '']
        if len(all_values) > maximum:
            self.all_exceptions.append(f'{key} has {len(all_values)} values but maximum is {maximum} on {row["source_identifier"]}.')
        if len(all_values) < minimum:
            self.all_exceptions.append(f'{key} has {len(all_values)} values but minimum is {minimum} on {row["model"]} on {row["source_identifier"]}.')
        return

    def check_range(self, key, value, row):
        all_values = [thing for thing in value.split(' | ') if thing != '']
        property_range = self.loaded_m3['properties'][key]['range']
        for value in all_values:
            if property_range == "http://www.w3.org/2001/XMLSchema#anyURI":
                if not(value.startswith('http')):
                    self.all_exceptions.append(f'{value} is not a URI for {row["source_identifier"]}.')
            else:
                if value.startswith('http:'):
                    self.all_exceptions.append(f'{value} may be a URI for {row["source_identifier"]}.')
        return

    def check_required_fields_are_present(self, row):
        for k , v in self.loaded_m3['properties'].items():
            if 'minimum' in v['cardinality']:
                if v['cardinality']['minimum'] > 0 and row['model'] in v['available_on']['class']:
                    keys = [key for key, value in row.items()]
                    if k not in keys:
                        self.all_exceptions.append(f'{row["source_identifier"]} has no {k} but {k} required on {row["model"]}')

    def iterate(self):
        for row in self.loaded_csv:
            self.validate_model(row)
            self.validate_values(row)
            self.validate_license(row)
            self.check_required_fields_are_present(row)
        separator = "\n"
        if len(self.all_exceptions) > 0:
            raise Exception(f"Migration spreadsheet has at least {len(self.all_exceptions)} problems: {separator.join(self.all_exceptions)}")
        else:
            print("Sheet passes all tests.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Choose sheet to validate..')
    parser.add_argument("-s", "--sheet", dest="sheet", help="Specify csv to test.", required=True)
    parser.add_argument("-p", "--profile", dest="profile", help="Specify a profile.", default="temp/utk.yml")
    args = parser.parse_args()
    x = ValidateMigration(
        profile=args.profile,
        migration_sheet=args.sheet
    )
    x.iterate()
