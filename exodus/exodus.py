from lxml import etree
import yaml


class Property:
    def __init__(self, path, namespaces):
        self.path = path
        self.namespaces = namespaces
        self.root = etree.parse(path)
        self.root_as_str = etree.tostring(self.root)

    def find(self, xpaths):
        all_values = []
        for xpath in xpaths:
            matches = self.root.xpath(xpath, namespaces=self.namespaces)
            for match in matches:
                all_values.append(match.text)
        return all_values


if __name__ == "__main__":
    x = yaml.safe_load(open("config.yml", "r"))
    local_identifiers = Property('fixtures/arrow_1.xml', {"mods": "http://www.loc.gov/mods/v3"}).find(x['local_name']['xpaths'])
    print(local_identifiers)

