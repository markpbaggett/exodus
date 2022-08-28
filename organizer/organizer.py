import csv
import requests
from tqdm import tqdm


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
        original_headers = [k for k, v in self.original_as_dict[0].items()]
        original_headers.append('rdf_type')
        return original_headers

    def __add_a_file(self, filename, row, preserve_and_obj=False):
        default_headings = ('source_identifier', 'model', 'remote_files', 'title', 'abstract', 'parents', 'rdf_type')
        initial_data = {
            'source_identifier': f"{row['source_identifier']}_{filename}",
            'model': "FileSet",
            'remote_files': f"https://digital.lib.utk.edu/collections/islandora/object/{row['source_identifier'].replace('_MODS.xml', '').replace('_', ':')}/datastream/{filename}",
            'title': self.__get_filename_title(filename, preserve_and_obj, row),
            'abstract': f"{filename} for {row['source_identifier']}",
            'parents': row['source_identifier'],
            'rdf_type': self.__get_rdf_types_for_file(filename, preserve_and_obj)
        }
        for k, v in row.items():
            if k not in default_headings:
                initial_data[k] = ''
        return initial_data

    @staticmethod
    def __get_filename_title(dsid, preserve_and_obj, row):
        if preserve_and_obj:
            identifier = row['local_identifier'].split('|')[0]
            if dsid == "OBJ":
                return f"{identifier}_i"
            elif dsid == "PRESERVE":
                return f"{identifier}_p"
            else:
                return dsid
        else:
            return dsid

    @staticmethod
    def __get_rdf_types_for_file(dsid, preserve_and_obj):
        if dsid == "OBJ" and preserve_and_obj is False:
            return "http://pcdm.org/use#PreservationFile|http://pcdm.org/use#IntermediateFile"
        elif dsid == "OBJ":
            return "http://pcdm.org/use#IntermediateFile"
        elif dsid == "PRESERVE":
            return "http://pcdm.org/use#PreservationFile"
        elif dsid == "MODS":
            return "http://pcdm.org/file-format-types#Markup"
        else:
            return ""

    def __add_files(self):
        new_csv_content = []
        for row in tqdm(self.original_as_dict):
            new_csv_content.append(row)
            pid = row['source_identifier'].replace('_MODS.xml', '').replace('_', ":")
            all_files = FileSetFinder(pid).files
            for dsid in all_files:
                if 'PRESERVE' in all_files and 'OBJ' in all_files:
                    new_csv_content.append(self.__add_a_file(dsid, row, True))
                else:
                    new_csv_content.append(self.__add_a_file(dsid, row))
        return new_csv_content

    def write_csv(self, filename):
        with open(filename, 'w', newline='') as bulkrax_sheet:
            writer = csv.DictWriter(bulkrax_sheet, fieldnames=self.headers)
            writer.writeheader()
            for data in self.new_csv_with_files:
                writer.writerow(data)
        return


class FileSetFinder:
    def __init__(self, pid):
        self.universal_ignores = ('DC', 'RELS-EXT', 'TECHMD', 'PREVIEW', 'TN', 'JPG', 'JP2')
        self.pid = pid
        self.files = self.__get_all_files()

    def __get_all_files(self):
        results = ResourceIndexSearch().get_files(self.pid)
        return [result for result in results if result not in self.universal_ignores]


class ResourceIndexSearch:
    def __init__(self, language="sparql", riformat="CSV", ri_endpoint="https://porter.lib.utk.edu/fedora/risearch"):
        self.risearch_endpoint = ri_endpoint
        self.valid_languages = ("itql", "sparql")
        self.valid_formats = ("CSV", "Simple", "Sparql", "TSV")
        self.language = self.validate_language(language)
        self.format = self.validate_format(riformat)
        self.base_url = (
            f"{self.risearch_endpoint}?type=tuples"
            f"&lang={self.language}&format={self.format}"
        )

    @staticmethod
    def escape_query(query):
        return (
            query.replace("*", "%2A")
                .replace(" ", "%20")
                .replace("<", "%3C")
                .replace(":", "%3A")
                .replace(">", "%3E")
                .replace("#", "%23")
                .replace("\n", "")
                .replace("?", "%3F")
                .replace("{", "%7B")
                .replace("}", "%7D")
                .replace("/", "%2F")
        )

    def validate_language(self, language):
        if language in self.valid_languages:
            return language
        else:
            raise Exception(
                f"Supplied language is not valid: {language}. Must be one of {self.valid_languages}."
            )

    def validate_format(self, user_format):
        if user_format in self.valid_formats:
            return user_format
        else:
            raise Exception(
                f"Supplied format is not valid: {user_format}. Must be one of {self.valid_formats}."
            )

    @staticmethod
    def __clean_csv_results(split_results, uri_prefix):
        results = []
        for result in split_results:
            if result.startswith(uri_prefix):
                new_result = result.split(",")
                results.append(
                    (new_result[0].replace(uri_prefix, ""), int(new_result[1]))
                )
        return sorted(results, key=lambda x: x[1])

    def get_files(self, pid):
        if self.language != "sparql":
            raise Exception(
                f"You must use sparql as the language for this method.  You used {self.language}."
            )
        sparql_query = self.escape_query(
            f"SELECT $files FROM <#ri> WHERE {{ <info:fedora/{pid}> "
            f"<info:fedora/fedora-system:def/view#disseminates> $files . }}"
        )
        results = requests.get(f"{self.base_url}&query={sparql_query}").content.decode('utf-8').split('\n')
        return [result.split('/')[-1] for result in results if result.startswith('info')]

    def __request_pids(self, request):
        results = requests.get(f"{self.base_url}&query={request}").content.decode('utf-8').split('\n')
        return [result.split('/')[-1] for result in results if result.startswith('info')]

    def get_images_no_parts(self, collection):
        members_of_collection_query = self.escape_query(
            f"""SELECT ?pid FROM <#ri> WHERE {{ ?pid <info:fedora/fedora-system:def/model#hasModel> <info:fedora/islandora:sp_large_image_cmodel> ; <info:fedora/fedora-system:def/relations-external#isMemberOfCollection> <info:fedora/{collection}> . }}"""
        )
        members_of_collection_parts_query = self.escape_query(
            f"""SELECT ?pid FROM <#ri> WHERE {{ ?pid <info:fedora/fedora-system:def/model#hasModel> <info:fedora/islandora:sp_large_image_cmodel> ; <info:fedora/fedora-system:def/relations-external#isMemberOfCollection> <info:fedora/{collection}> ; <info:fedora/fedora-system:def/relations-external#isConstituentOf> ?unknown. }}"""
        )
        members_of_collection = self.__request_pids(members_of_collection_query)
        members_of_collection_parts = self.__request_pids(members_of_collection_parts_query)
        members_of_collection_no_parts = [pid for pid in members_of_collection if pid not in members_of_collection_parts]
        return members_of_collection_no_parts


if __name__ == "__main__":
    """Take a CSV and Add files to it"""
    x = FileOrganizer('temp/test_csboyd_mods_initial.csv')
    x.write_csv('temp/test_csboyd_mods_initial_with_files_remote2.csv')
    """Below: Get datastreams of a PID without the ones to ignore"""
    # x = FileSetFinder('brehm:3')
    # print(x.files)
    """Below: Get Large Images from a Collection with on constituent parts of a compound object"""
    # x = ResourceIndexSearch().get_images_no_parts('collections:boydcs')
    # with open('temp/things_to_download.txt', 'w') as things_to_download:
    #     for pid in x:
    #         things_to_download.write(f"{pid}\n")
