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


class MetadataMapping:
    def __init__(self, path_to_mapping):
        self.path = path_to_mapping
        self.output_data = {}
        self.mapping_data = yaml.safe_load(open(path_to_mapping, "r"))['mapping']

    def execute(self):
        output_data = {}
        for rdf_property in self.mapping_data:
            output_data[rdf_property['name']] = Property(
                'fixtures/arrow_1.xml',
                {"mods": "http://www.loc.gov/mods/v3"}
            ).find(rdf_property['xpaths'])
        return output_data


if __name__ == "__main__":
    test = MetadataMapping('config.yml')
    print(test.execute())

