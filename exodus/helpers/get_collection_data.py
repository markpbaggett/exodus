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
            "xlink": "http://www.w3.org/1999/xlink",
        }

    def __simplify_xpath(self, xpath):
        return " | ".join([value.text for value in self.mods.xpath(xpath, namespaces=self.namespaces)])

    def __get_valueURIs(self, xpath):
        return " | ".join([value for value in self.mods.xpath(xpath, namespaces=self.namespaces)])

    def __get_valueURIs_from_multiple_xpaths(self, xpaths):
        all_matches = []
        for xpath in xpaths:
            all_matches.extend([value for value in self.mods.xpath(xpath, namespaces=self.namespaces)])
        return " | ".join(all_matches)

    def __get_text_from_multiple_xpaths(self, xpaths):
        all_matches = []
        for xpath in xpaths:
            all_matches.extend([value.text for value in self.mods.xpath(xpath, namespaces=self.namespaces)])
        return " | ".join(all_matches)

    def grab_all_metadata(self):
        return {
            "source_identifier": self.pid,
            "model": "Collection",
            "parents": "",
            "title": self.__simplify_xpath('mods:titleInfo/mods:title'),
            "abstract": self.__simplify_xpath('mods:abstract'),
            "contributor": self.__get_valueURIs_from_multiple_xpaths(
                [
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Contributor")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Addressee")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Arranger")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Associated Name")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Autographer")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Censor")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Choreographer")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Client")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Contractor")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Copyright Holder")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Dedicatee")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Depicted")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Distributor")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Donor")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Editor")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Editor of Compilation")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Former Owner")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Honoree")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Host Institution")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Instrumentalist")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Interviewer")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Issuing Body")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Music Copyist")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Musical Director")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Organizer")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Originator")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Owner")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Performer")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Printer")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Printer of Plates")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Producer")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Production Company")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Publisher")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Restorationist")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Set Designer")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Signer")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Speaker")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Stage Director")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Stage Manager")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Standards Body")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Surveyor")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Translator")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Videographer")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Witness")]]/@valueURI'
                ]
            ),
            "utk_contributor": self.__get_text_from_multiple_xpaths(
                [
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Contributor")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Addressee")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Arranger")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Associated Name")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Autographer")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Censor")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Choreographer")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Client")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Contractor")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Copyright Holder")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Dedicatee")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Depicted")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Distributor")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Donor")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Editor")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Editor of Compilation")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Former Owner")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Honoree")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Host Institution")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Instrumentalist")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Interviewer")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Issuing Body")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Music Copyist")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Musical Director")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Organizer")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Originator")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Owner")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Performer")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Printer")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Printer of Plates")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Producer")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Production Company")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Publisher")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Restorationist")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Set Designer")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Signer")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Speaker")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Stage Director")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Stage Manager")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Standards Body")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Surveyor")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Translator")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Videographer")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Witness")]]/mods:namePart'
                ]
            ),
            "creator": self.__get_valueURIs_from_multiple_xpaths(
                [
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Creator")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Architect")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Artist")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Attributed Name")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Author")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Binding Designer")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Cartographer")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Compiler")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Composer")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Correspondent")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Costume Designer")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Designer")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Engraver")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Illustrator")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Interviewee")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Lithographer")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Lyricist")]]/@valueURI',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Photographer")]]/@valueURI'
                ]
            ),
            "utk_creator": self.__get_text_from_multiple_xpaths(
                [
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Creator")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Architect")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Artist")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Attributed Name")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Author")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Binding Designer")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Cartographer")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Compiler")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Composer")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Correspondent")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Costume Designer")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Designer")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Engraver")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Illustrator")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Interviewee")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Lithographer")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Lyricist")]]/mods:namePart',
                    'mods:name[not(@valueURI)][mods:role/mods:roleTerm[contains(.,"Photographer")]]/mods:namePart'
                ]
            ),
            "date_created": self.__simplify_xpath('mods:originInfo/mods:dateCreated[not(@encoding)]'),
            "date_issued": self.__simplify_xpath('mods:originInfo/mods:dateIssued[not(@encoding)]'),
            "date_created_d": self.__simplify_xpath('mods:originInfo/mods:dateCreated[@encoding]'),
            "date_issued_d": self.__simplify_xpath('mods:originInfo/mods:dateIssued[@encoding]'),
            "utk_publisher": self.__simplify_xpath('mods:originInfo/mods:publisher[not(@valueURI)]'),
            "publisher": self.__get_valueURIs('mods:originInfo/mods:publisher/@valueURI'),
            "publication_place": self.__simplify_xpath('mods:originInfo/mods:place/mods:placeTerm[@valueURI]'),
            "extent": self.__simplify_xpath('mods:physicalDescription/mods:extent'),
            "form": self.__get_valueURIs('mods:physicalDescription/mods:form/@valueURI'),
            "subject": self.__get_valueURIs_from_multiple_xpaths(
                [
                    'mods:subject/mods:topic/@valueURI',
                    'mods:subject[mods:topic]/@valueURI'
                ]
            ),
            "keyword": self.__simplify_xpath('mods:subject[not(@valueURI)]/mods:topic'),
            "spatial": self.__get_valueURIs_from_multiple_xpaths(
                [
                    'mods:subject/mods:geographic/@valueURI',
                    'mods:subject[mods:geographic]/@valueURI'
                ]
            ),
            "resource_type": "",
            "repository": self.__get_valueURIs('mods:location/mods:physicalLocation/@valueURI'),
            "note": self.__simplify_xpath('mods:note')
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
