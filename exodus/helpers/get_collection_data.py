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


if __name__ == "__main__":
    print(CollectionMetadata('collections:boydcs').get_keyword())