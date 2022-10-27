import requests
from lxml import etree
from io import BytesIO


class CollectionMetadata:
    def __init__(self, pid):
        self.mods = self.__get_metadata(pid)
        self.namespaces = {
            "mods": "http://www.loc.gov/mods/v3",
            "xlink": "http://www.w3.org/1999/xlink"
        }

    def __simplify_xpath(self, xpath):
        return [value.text for value in self.mods.xpath(xpath, namespaces=self.namespaces)]

    def __grab_all(self):
        return {
            "title": self.get_titles(),
            "abstract": self.get_abstract(),
            "contributor": "",
            "utk_contributor": "",
            "creator": "",
            "utk_creator": "",
            "date_created": self.get_date_created(),
            "date_issued": self.get_date_issued(),
            "date_created_d": self.get_date_created_d(),
            "date_issued_d": self.get_date_issued_d(),
            "utk_publisher": self.get_local_publisher(),
            "publisher": self.get_publisher(),
            "publication_place": self.get_publication_place_term(),
            "extent": self.get_extent(),
            "form": self.__simplify_xpath('mods:physicalDescription/mods:form[@valueURI]'),
            "subject": "",
            "keyword": "",
            "spatial": "",
            "resource_type": "",
            "repository": "",
            "note": "",
            "collection_link": ""
        }

    @staticmethod
    def __get_metadata(pid):
        r = requests.get(f"https://digital.lib.utk.edu/collections/islandora/object/{pid}/datastream/MODS")
        return etree.parse(BytesIO(r.content))

    def get_titles(self):
        return [value.text for value in self.mods.xpath('mods:titleInfo/mods:title', namespaces=self.namespaces)]

    def get_abstract(self):
        return [value.text for value in self.mods.xpath('mods:abstract', namespaces=self.namespaces)]

    def get_creators(self):
        # TODO: Fix once fully defined.
        return [value.text for value in self.mods.xpath('mods:name[mods:role/mods:roleTerm[contains(.,"Photographer")]]/mods:namePart', namespaces=self.namespaces)]

    def get_date_created(self):
        return self.__simplify_xpath('mods:originInfo/mods:dateCreated[not(@edtf)]')

    def get_date_issued(self):
        return self.__simplify_xpath('mods:originInfo/mods:dateIssued[not(@edtf)]')

    def get_date_created_d(self):
        return self.__simplify_xpath('mods:originInfo/mods:dateCreated[@edtf]')

    def get_date_issued_d(self):
        return self.__simplify_xpath('mods:originInfo/mods:dateIssued[@edtf]')

    def get_local_publisher(self):
        return self.__simplify_xpath('mods:originInfo/mods:publisher[not(@valueURI)]')

    def get_publisher(self):
        return self.__simplify_xpath('mods:originInfo/mods:publisher/@valueURI')

    def get_publication_place_term(self):
        return self.__simplify_xpath('mods:originInfo/mods:place/mods:placeTerm[@valueURI]')

    def get_extent(self):
        return self.__simplify_xpath('mods:physicalDescription/mods:extent')

    def get_keyword(self):
        return self.__simplify_xpath('mods:subject[not(@valueURI)]/mods:topic OR mods:subject[not(@valueURI)]/mods:name/mods:namePart OR mods:subject/mods:name[not(@valueURI)]/mods:namePart OR mods:subject/mods:topic[not(@valueURI)]')

    def get_resource_type(self):
        return self.__simplify_xpath('mods:typeOfResource')

    def get_repository(self):
        return self.__simplify_xpath('mods:location/mods:physicalLocation[@valueURI]')

    def get_note(self):
        return self.__simplify_xpath('mods:note')


if __name__ == "__main__":
    print(CollectionMetadata('collections:boydcs').get_keyword())