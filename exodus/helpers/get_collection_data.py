import requests
from lxml import etree
from io import BytesIO
import csv


class CollectionMetadata:
    def __init__(self, pid):
        self.pid = pid
        self.mods = self.__get_metadata(pid)
        self.namespaces = {
            "mods": "http://www.loc.gov/mods/v3",
            "xlink": "http://www.w3.org/1999/xlink"
        }

    def __simplify_xpath(self, xpath):
        return " | ".join([value.text for value in self.mods.xpath(xpath, namespaces=self.namespaces)])

    def grab_all_metadata(self):
        return {
            "source_identifier": self.pid,
            "model": "Collection",
            "parents": "",
            "title": self.__simplify_xpath('mods:titleInfo/mods:title'),
            "abstract": self.__simplify_xpath('mods:abstract'),
            "contributor": "",
            "utk_contributor": "",
            "creator": "",
            "utk_creator": "",
            "date_created": self.__simplify_xpath('mods:originInfo/mods:dateCreated[not(@edtf)]'),
            "date_issued": self.__simplify_xpath('mods:originInfo/mods:dateIssued[not(@edtf)]'),
            "date_created_d": self.__simplify_xpath('mods:originInfo/mods:dateCreated[@edtf]'),
            "date_issued_d": self.__simplify_xpath('mods:originInfo/mods:dateIssued[@edtf]'),
            "utk_publisher": self.__simplify_xpath('mods:originInfo/mods:publisher[not(@valueURI)]'),
            "publisher": self.__simplify_xpath('mods:originInfo/mods:publisher/@valueURI'),
            "publication_place": self.__simplify_xpath('mods:originInfo/mods:place/mods:placeTerm[@valueURI]'),
            "extent": self.__simplify_xpath('mods:physicalDescription/mods:extent'),
            "form": self.__simplify_xpath('mods:physicalDescription/mods:form[@valueURI]'),
            "subject": "",
            "keyword": "",
            "spatial": "",
            "resource_type": self.__simplify_xpath('mods:typeOfResource'),
            "repository": self.__simplify_xpath('mods:location/mods:physicalLocation[@valueURI]'),
            "note": self.__simplify_xpath('mods:note'),
            "collection_link": ""
        }

    @staticmethod
    def __get_metadata(pid):
        r = requests.get(f"https://digital.lib.utk.edu/collections/islandora/object/{pid}/datastream/MODS")
        return etree.parse(BytesIO(r.content))

    def get_creators(self):
        # TODO: Fix once fully defined.
        return [value.text for value in self.mods.xpath('mods:name[mods:role/mods:roleTerm[contains(.,"Photographer")]]/mods:namePart', namespaces=self.namespaces)]


class CollectionOrganizer:
    def __init__(self, csv):
        self.original_csv = csv
        self.original_as_dict = self.__read()
        self.unique_collections = self.__build_collections()
        self.headers = self.__get_headers()

    def __read(self):
        csv_content = []
        with open(self.original_csv, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                csv_content.append(row)
        return csv_content

    def __get_headers(self):
        original_headers = [k for k, v in self.original_as_dict[0].items()]
        collection_headers = [k for k, v in self.unique_collections[0].items()]
        for header in collection_headers:
            if header not in original_headers:
                original_headers.append(header)
        return original_headers

    def __get_unique_collections(self):
        unique_collections = []
        work_types = ('Image', 'Video', 'Audio')
        for thing in self.original_as_dict:
            if thing['model'] in work_types:
                if thing['parents'] not in unique_collections:
                    unique_collections.append(thing['parents'])
        return unique_collections

    def __build_collections(self):
        return [CollectionMetadata(collection).grab_all_metadata() for collection in self.__get_unique_collections()]

    def write_csv(self, filename):
        with open(filename, 'w', newline='') as bulkrax_sheet:
            writer = csv.DictWriter(bulkrax_sheet, fieldnames=self.headers)
            writer.writeheader()
            for data in self.original_as_dict:
                writer.writerow(data)
            for data in self.unique_collections:
                writer.writerow(data)
        return


if __name__ == "__main__":
    CollectionOrganizer('temp/gamble_with_filesets_and_attachments.csv').write_csv('temp/gamble_with_collections.csv')
