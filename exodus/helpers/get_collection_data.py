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

    def __get_valueURIs(self, xpath):
        return " | ".join([value for value in self.mods.xpath(xpath, namespaces=self.namespaces)])

    def grab_all_metadata(self):
        return {
            "source_identifier": self.pid,
            "model": "Collection",
            "parents": "",
            "title": self.__simplify_xpath('mods:titleInfo/mods:title'),
            "abstract": self.__simplify_xpath('mods:abstract'),
            "contributor": __get_valueURIs('mods:name[mods:role/mods:roleTerm[contains(.,"Contributor")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Addressee")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Arranger")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Associated Name")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Autographer")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Censor")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Choreographer")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Client")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Contractor")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Copyright Holder")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Dedicatee")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Depicted")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Distributor")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Donor")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Editor")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Editor of Compilation")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Former Owner")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Honoree")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Host Institution")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Instrumentalist")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Interviewer")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Issuing Body")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Music Copyist")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Musical Director")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Organizer")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Originator")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Owner")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Performer")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Printer")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Printer of Plates")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Producer")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Production Company")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Publisher")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Restorationist")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Set Designer")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Signer")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Speaker")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Stage Director")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Stage Manager")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Standards Body")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Surveyor")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Translator")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Videographer")]]/@valueURI' OR 'mods:name[mods:role/mods:roleTerm[contains(.,"Witness")]]/@valueURI'),
            "utk_contributor": __simplify_xpath('mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Contributor")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Addressee")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Arranger")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Associated Name")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Autographer")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Censor")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Choreographer")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Client")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Contractor")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Copyright Holder")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Dedicatee")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Depicted")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Distributor")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Donor")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Editor")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Editor of Compilation")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Former Owner")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Honoree")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Host Institution")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Instrumentalist")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Interviewer")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Issuing Body")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Music Copyist")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Musical Director")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Organizer")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Originator")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Owner")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Performer")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Printer")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Printer of Plates")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Producer")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Production Company")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Publisher")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Restorationist")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Set Designer")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Signer")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Speaker")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Stage Director")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Stage Manager")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Standards Body")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Surveyor")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Translator")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Videographer")]]/mods:namePart' OR 'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Witness")]]/mods:namePart'),
            "creator": self.__get_valueURIs('mods:name[role/roleTerm[contains(.,"Creator")]]/@valueURI' OR 'mods:name[role/roleTerm[contains(.,"Architect")]]/@valueURI' OR 'mods:name[role/roleTerm[contains(.,"Artist")]]/@valueURI' OR 'mods:name[role/roleTerm[contains(.,"Attributed Name")]]/@valueURI' OR 'mods:name[role/roleTerm[contains(.,"Author")]]/@valueURI' OR 'mods:name[role/roleTerm[contains(.,"Binding Designer")]]/@valueURI' OR 'mods:name[role/roleTerm[contains(.,"Cartographer")]]/@valueURI' OR 'mods:name[role/roleTerm[contains(.,"Compiler")]]/@valueURI' OR 'mods:name[role/roleTerm[contains(.,"Composer")]]/@valueURI' OR 'mods:name[role/roleTerm[contains(.,"Correspondent")]]/@valueURI' OR 'mods:name[role/roleTerm[contains(.,"Costume Designer")]]/@valueURI' OR 'mods:name[role/roleTerm[contains(.,"Designer")]]/@valueURI' OR 'mods:name[role/roleTerm[contains(.,"Engraver")]]/@valueURI' OR 'mods:name[role/roleTerm[contains(.,"Illustrator")]]/@valueURI' OR 'mods:name[role/roleTerm[contains(.,"Interviewee")]]/@valueURI' OR 'mods:name[role/roleTerm[contains(.,"Lithographer")]]/@valueURI' OR 'mods:name[role/roleTerm[contains(.,"Lyricist")]]/@valueURI' OR 'mods:name[role/roleTerm[contains(.,"Photographer")]]/@valueURI'),
            "utk_creator": self.__simplify_xpath('mods:name[not(@valueURI)][role/roleTerm[contains(.,"Creator")]]/mods:namePart' OR 'mods:name[not(@valueURI)][role/roleTerm[contains(.,"Architect")]]/mods:namePart' OR 'mods:name[not(@valueURI)][role/roleTerm[contains(.,"Artist")]]/mods:namePart' OR 'mods:name[not(@valueURI)][role/roleTerm[contains(.,"Attributed Name")]]/mods:namePart' OR 'mods:name[not(@valueURI)][role/roleTerm[contains(.,"Author")]]/mods:namePart' OR 'mods:name[not(@valueURI)][role/roleTerm[contains(.,"Binding Designer")]]/mods:namePart' OR 'mods:name[not(@valueURI)][role/roleTerm[contains(.,"Cartographer")]]/mods:namePart' OR 'mods:name[not(@valueURI)][role/roleTerm[contains(.,"Compiler")]]/mods:namePart' OR 'mods:name[not(@valueURI)][role/roleTerm[contains(.,"Composer")]]/mods:namePart' OR 'mods:name[not(@valueURI)][role/roleTerm[contains(.,"Correspondent")]]/mods:namePart' OR 'mods:name[not(@valueURI)][role/roleTerm[contains(.,"Costume Designer")]]/mods:namePart' OR 'mods:name[not(@valueURI)][role/roleTerm[contains(.,"Designer")]]/mods:namePart' OR 'mods:name[not(@valueURI)][role/roleTerm[contains(.,"Engraver")]]/mods:namePart' OR 'mods:name[not(@valueURI)][role/roleTerm[contains(.,"Illustrator")]]/mods:namePart' OR 'mods:name[not(@valueURI)][role/roleTerm[contains(.,"Interviewee")]]/mods:namePart' OR 'mods:name[not(@valueURI)][role/roleTerm[contains(.,"Lithographer")]]/mods:namePart' OR 'mods:name[not(@valueURI)][role/roleTerm[contains(.,"Lyricist")]]/mods:namePart' OR 'mods:name[not(@valueURI)][role/roleTerm[contains(.,"Photographer")]]/mods:namePart'),
            "date_created": self.__simplify_xpath('mods:originInfo/mods:dateCreated[not(@edtf)]'),
            "date_issued": self.__simplify_xpath('mods:originInfo/mods:dateIssued[not(@edtf)]'),
            "date_created_d": self.__simplify_xpath('mods:originInfo/mods:dateCreated[@edtf]'),
            "date_issued_d": self.__simplify_xpath('mods:originInfo/mods:dateIssued[@edtf]'),
            "utk_publisher": self.__simplify_xpath('mods:originInfo/mods:publisher[not(@valueURI)]'),
            "publisher": self.__get_valueURIs('mods:originInfo/mods:publisher/@valueURI'),
            "publication_place": self.__simplify_xpath('mods:originInfo/mods:place/mods:placeTerm[@valueURI]'),
            "extent": self.__simplify_xpath('mods:physicalDescription/mods:extent'),
            "form": self.__get_valueURIs('mods:physicalDescription/mods:form/@valueURI'),
            "subject": self.__get_valueURIs('mods:subject[mods:topic]/@valueURI'),
            "keyword": self.__simplify_xpath('mods:subject[not(@valueURI)]/mods:topic'),
            "spatial": self.__get_valueURIs('mods:subject/mods:geographic/@valueURI'),
            "resource_type": "",
            "repository": self.__get_valueURIs('mods:location/mods:physicalLocation/@valueURI'),
            "note": self.__simplify_xpath('mods:note')
        }

    @staticmethod
    def __get_metadata(pid):
        r = requests.get(f"https://digital.lib.utk.edu/collections/islandora/object/{pid}/datastream/MODS")
        return etree.parse(BytesIO(r.content))

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
    import argparse
    parser = argparse.ArgumentParser(description='Add collections to sheet.')
    parser.add_argument("-s", "--sheet", dest="sheet", help="Specify the initial sheet.", required=True)
    parser.add_argument(
        "-c", "--collections_sheet", dest="collections_sheet", help="Optional: specify collections sheet."
    )
    args = parser.parse_args()
    collections_sheet = f"{args.sheet.replace('.csv', '')}_with_collections.csv"
    if args.collections_sheet:
        collections_sheet = args.collections_sheet
    CollectionOrganizer(
        args.sheet
    ).write_csv(
        collections_sheet
    )
