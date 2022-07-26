from lxml import etree


class Property:
    def __init__(self, path, namespaces):
        self.path = path
        self.namespaces = namespaces
        self.root = etree.parse(path)
        self.root_as_str = etree.tostring(self.root)

    def find(self, xpath):
        all_identifiers = self.root.xpath(xpath, namespaces=self.namespaces)
        for identifier in all_identifiers:
            print(identifier.text)


if __name__ == "__main__":
    Property('fixtures/arrow_1.xml', {"mods": "http://www.loc.gov/mods/v3"}).find('//mods:identifier[@type="pid"]')
