from lxml import etree
import yaml
import xmltodict


class BaseProperty:
    def __init__(self, path, namespaces):
        self.path = path
        self.namespaces = namespaces
        self.root = etree.parse(path)
        self.root_as_str = etree.tostring(self.root)


class StandardProperty(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find(self, xpaths):
        all_values = []
        for xpath in xpaths:
            matches = self.root.xpath(xpath, namespaces=self.namespaces)
            for match in matches:
                all_values.append(match.text)
        return all_values


class TitleProperty(BaseProperty):
    """
    Used for Titles.

    If just `titleInfo/title`, map to dcterms:title.

    If just `titleInfo[@supplied="yes"]/title`, map to dcterms:title.

    If `titleInfo[@supplied="yes"]/title` and `titleInfo/title`, map the former to dcterms:title, and the latter to
    dcterms:alternative.

    If `titleInfo/partName`, concat to `titleInfo/title` in dcterms:title with a `,`.

    If `titleInfo/partNumber`, concat to `titleInfo[@supplied="yes"]` in dcterms:alternative (this is going to be hard).

    If `titleInfo/nonSort`, concat to `titleInfo/title` in dcterms:title.

    If `titleInfo[@type="alternative"]`, map to dcterms:alternative.
    """
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)
        self.various_titles = {}

    def __find_plain_titles(self):
        self.various_titles['plain'] = [thing.text for thing in self.root.xpath(
            'mods:titleInfo[not(@supplied)]/mods:title',
            namespaces=self.namespaces
        )]
        return

    def __find_supplied_titles(self):
        self.various_titles['supplied'] = [thing.text for thing in self.root.xpath(
            'mods:titleInfo[@supplied]/mods:title',
            namespaces=self.namespaces
        )]
        return

    def __find_part_names(self):
        self.various_titles['part_names'] = [thing.text for thing in self.root.xpath(
            'mods:titleInfo/mods:partName',
            namespaces=self.namespaces
        )]
        return

    def __find_part_numbers(self):
        self.various_titles['part_numbers'] = [thing.text for thing in self.root.xpath(
            'mods:titleInfo/mods:partNumber',
            namespaces=self.namespaces
        )]
        return

    def __find_non_sorts(self):
        self.various_titles['non_sorts'] = [thing.text for thing in self.root.xpath(
            'mods:titleInfo/mods:nonSort',
            namespaces=self.namespaces
        )]
        return

    def __find_alternatives(self):
        self.various_titles['alternatives'] = [thing.text for thing in self.root.xpath(
            'mods:titleInfo[@type="alternative"]/mods:title',
            namespaces=self.namespaces
        )]
        return

    def find(self):
        self.__find_plain_titles()
        self.__find_supplied_titles()
        self.__find_non_sorts()
        self.__find_part_numbers()
        self.__find_part_names()
        self.__find_alternatives()
        # TODO: for now, just handle supplied, alternatives, and normal titles.
        titles = []
        alternatives = []
        if len(self.various_titles['supplied']) > 0 and len(self.various_titles['plain']) > 0:
            for title in self.various_titles['supplied']:
                titles.append(title)
            for title in self.various_titles['plain']:
                alternatives.append(title)
        else:
            for title in self.various_titles['supplied']:
                titles.append(title)
            for title in self.various_titles['plain']:
                titles.append(title)
        for title in self.various_titles['alternatives']:
            alternatives.append(title)
        return {'title': titles, 'alternative_title': alternatives}


class MetadataMapping:
    def __init__(self, path_to_mapping):
        self.path = path_to_mapping
        self.output_data = {}
        self.mapping_data = yaml.safe_load(open(path_to_mapping, "r"))['mapping']

    def execute(self, file, namespaces):
        output_data = {}
        for rdf_property in self.mapping_data:
            if 'special' not in rdf_property:
                output_data[rdf_property['name']] = StandardProperty(
                    file,
                    namespaces
                ).find(rdf_property['xpaths'])
            else:
                special = self.__lookup_special_property(rdf_property['special'], file, namespaces)
                for k, v in special.items():
                    output_data[k] = v
        return output_data

    @staticmethod
    def __lookup_special_property(special_property, file, namespaces):
        special_properties = {
            "TitleProperty": TitleProperty(file, namespaces).find(),
            "NameProperty": NameProperty(file).find()
        }
        return special_properties[special_property]


class NameProperty:
    def __init__(self, file):
        self.path = file
        self.namespaces = {"http://www.loc.gov/mods/v3": "mods"}
        self.all_names = self.__find_all_names()

    def __find_all_names(self):
        with open(self.path) as fd:
            doc = xmltodict.parse(fd.read(), process_namespaces=True, namespaces=self.namespaces)
            all_names = doc['mods:mods']['mods:name']
            if type(all_names) == list:
                return all_names
            elif type(all_names) == dict:
                return [all_names]
            elif type(all_names) == str:
                return [all_names]
            else:
                return ['Problem']

    def find(self):
        roles_and_names = {}
        for name in self.all_names:
            role = name['mods:role']['mods:roleTerm']['#text']
            name_value = name['mods:namePart']
            if '@valueURI' in name:
                name_value = name['@valueURI']
            if role not in roles_and_names:
                roles_and_names[role] = [name_value]
            else:
                roles_and_names[role].append(name_value)
        return roles_and_names


if __name__ == "__main__":
    test = MetadataMapping('configs/utk_dc.yml')
    print(test.execute('fixtures/arrow_1.xml', {"mods": "http://www.loc.gov/mods/v3"}))

