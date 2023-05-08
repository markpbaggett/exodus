from lxml import etree
import yaml
import xmltodict
import os
import csv
from tqdm import tqdm
from helpers import *


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
                if not xpath.endswith('@xlink:href') and match.text is not None:
                    all_values.append(match.text)
                elif xpath.endswith('@xlink:href'):
                    all_values.append(match)
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
            'mods:titleInfo[not(@supplied)][not(@type="alternative")]/mods:title',
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
        # TODO: Gross!  This had so many needless side effects.  Fix!
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


class XMLtoDictProperty:
    def __init__(self, file):
        self.path = file
        self.namespaces = {"http://www.loc.gov/mods/v3": "mods", "http://www.w3.org/1999/xlink": "xlink"}
        self.doc = self.__get_doc(file)

    def __get_doc(self, path):
        with open(path) as fd:
            return xmltodict.parse(fd.read(), process_namespaces=True, namespaces=self.namespaces)


class RoleAndNameProperty(XMLtoDictProperty):
    def __init__(self, file):
        super().__init__(file)
        self.all_names = self.__find_all_names()

    def __find_all_names(self):
        if 'mods:name' in self.doc['mods:mods']:
            all_names = self.doc['mods:mods']['mods:name']
            if type(all_names) == list:
                return all_names
            elif type(all_names) == dict:
                return [all_names]
            elif type(all_names) == str:
                return [all_names]
            else:
                return ['Problem']
        else:
            return []

    def find(self):
        roles_and_names = {}
        for name in self.all_names:
            local_roles = []
            try:
                local_roles.append(f"utk_{name['mods:role']['mods:roleTerm']['#text'].lower().replace(' ', '_')}")
            except KeyError:
                print(name)
            # TODO: A name can have multiple roles
            except TypeError:
                for role in name['mods:role']:
                    local_roles.append(f"utk_{role['mods:roleTerm']['#text'].lower().replace(' ', '_')}")
            # TODO: Rework this.  It's not pretty but it works.
            name_value = name['mods:namePart']
            for role in local_roles:
                if type(name_value) is list:
                    for part in name_value:
                        if type(part) is dict and part.get('mods:namePart'):
                            if role not in roles_and_names:
                                roles_and_names[role] = [part['mods:namePart']]
                            else:
                                roles_and_names[role].append([part['mods:namePart']])
                        if type(part) is str and not part.startswith('http'):
                            if role not in roles_and_names:
                                roles_and_names[role] = [part]
                            else:
                                roles_and_names[role].append(part)
                elif role not in roles_and_names and not name_value.startswith('http'):
                    roles_and_names[role] = [name_value]
                elif not name_value.startswith('http'):
                    roles_and_names[role].append(name_value)
        return roles_and_names


class NameProperty(XMLtoDictProperty):
    """
    Used for names.
    """
    def __init__(self, file):
        super().__init__(file)
        self.all_names = self.__find_all_names()

    def __find_all_names(self):
        if 'mods:name' in self.doc['mods:mods']:
            all_names = self.doc['mods:mods']['mods:name']
            if type(all_names) == list:
                return all_names
            elif type(all_names) == dict:
                return [all_names]
            elif type(all_names) == str:
                return [all_names]
            else:
                return ['Problem']
        else:
            return []

    def find(self):
        roles_and_names = {}
        for name in self.all_names:
            roles = []
            local_roles = []
            try:
                roles.append(name['mods:role']['mods:roleTerm']['#text'].lower().replace(' ', '_'))
                local_roles.append(f"utk_{name['mods:role']['mods:roleTerm']['#text'].lower().replace(' ', '_')}")
            except KeyError:
                print(name)
            # TODO: A name can have multiple roles
            except TypeError:
                for role in name['mods:role']:
                    roles.append(role['mods:roleTerm']['#text'].lower().replace(' ', '_'))
                    local_roles.append(f"utk_{role['mods:roleTerm']['#text'].lower().replace(' ', '_')}")
            # TODO: Rework this.  It's not pretty but it works.
            name_value = name['mods:namePart']
            if '@valueURI' in name:
                name_value = name['@valueURI']
            for role in roles:
                if type(name_value) is list:
                    for part in name_value:
                        if type(part) is dict and '@valueURI' in part:
                            if role not in roles_and_names:
                                roles_and_names[role] = [part['@valueURI']]
                            else:
                                roles_and_names[role].append([part['@valueURI']])
                elif role not in roles_and_names and name_value.startswith('http'):
                    roles_and_names[role] = [name_value]
                elif name_value.startswith('http'):
                    roles_and_names[role].append(name_value)
            for role in local_roles:
                if type(name_value) is list:
                    for part in name_value:
                        if type(part) is str and not part.startswith('http'):
                            if role not in roles_and_names:
                                roles_and_names[role] = [part]
                            else:
                                roles_and_names[role].append(part)
                elif role not in roles_and_names and not name_value.startswith('http'):
                    roles_and_names[role] = [name_value]
                elif not name_value.startswith('http'):
                    roles_and_names[role].append(name_value)
        return roles_and_names


class GeoNamesProperty(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find(self, name):
        uris = [
            uri.replace('about.rdf', '')
            for uri in self.root.xpath('mods:subject/mods:geographic/@valueURI', namespaces=self.namespaces)
        ]
        lc_uris = [
            uri
            for uri in self.root.xpath('mods:subject[mods:geographic]/@valueURI', namespaces=self.namespaces)
        ]
        all_values = []
        for uri in lc_uris:
            all_values.append(uri)
        for uri in uris:
            all_values.append(uri)
        return {name: all_values}


class PhysicalLocationsProperties(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def __find_repositories(self):
        with_repository_designation = [
            thing.text
            for thing in self.root.xpath(
                'mods:location/mods:physicalLocation[@displayLabel="Repository"]',
                namespaces=self.namespaces
            )
        ]
        others = [
            thing.text
            for thing in self.root.xpath
            (
                'mods:location/mods:physicalLocation[not(@displayLabel)]',
                namespaces=self.namespaces
            )
        ]
        all_repositories = []
        for value in with_repository_designation:
            all_repositories.append(value)
        for value in others:
            if value is None or "University of Tennesse" in value:
                all_repositories.append("University of Tennessee, Knoxville. Special Collections")
            else:
                all_repositories.append(value)
        return all_repositories

    def find(self):
        return {
            'repository': self.__find_repositories(),
            'archival_collection': self.__find_archival_collections(),
        }

    def __find_archival_collections(self):
        all_archival_collections = []
        other_archival_collections = [
            collection.text for collection in self.root.xpath(
                'mods:location/mods:physicalLocation[@displayLabel="Collection"]',
                namespaces=self.namespaces
            )
        ]
        primary_archival_collections = [
            collection for collection in self.root.xpath(
                'mods:relatedItem[@displayLabel="Collection"][mods:titleInfo]',
                namespaces=self.namespaces
            )
        ]
        for collection in other_archival_collections:
            if collection not in all_archival_collections:
                all_archival_collections.append(collection)
        for collection in primary_archival_collections:
            identifier = ""
            title = ""
            output = ""
            for child in collection:
                if child.tag == f"{{http://www.loc.gov/mods/v3}}identifier":
                    identifier = child.text
                elif child.tag == f"{{http://www.loc.gov/mods/v3}}titleInfo":
                    for sub_child in child:
                        if sub_child.tag == f"{{http://www.loc.gov/mods/v3}}title":
                            title = sub_child.text
            if title != "" and identifier != "":
                output = f"{title}, {identifier}"
            elif identifier != "":
                output = identifier
            elif title != "":
                output = title
            if output != "":
                all_archival_collections.append(output)
        return all_archival_collections


class DataProvider(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find(self):
        values = [
            value.text
            for value in self.root.xpath('mods:recordInfo/mods:recordContentSource', namespaces=self.namespaces)
        ]
        return {
            "provider": ["University of Tennessee, Knoxville. Libraries"],
            "intermediate_provider": [value for value in values if value != "University of Tennessee, Knoxville. Libraries"]
        }


class MachineDate(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find(self):
        date_created = [
            value.text
            for value in self.root.xpath('mods:originInfo/mods:dateCreated[@encoding="edtf"]', namespaces=self.namespaces)
        ]
        date_issued = [
            value.text
            for value in
            self.root.xpath('mods:originInfo/mods:dateIssued[@encoding="edtf"]', namespaces=self.namespaces)
        ]
        date_other = [
            value.text
            for value in
            self.root.xpath('mods:originInfo/mods:dateOther[@encoding="edtf"]', namespaces=self.namespaces)
        ]
        return {
            "date_created_d": self.__sort_if_range(date_created),
            "date_issued_d": self.__sort_if_range(date_issued),
            "date_other_d": self.__sort_if_range(date_other),
        }

    @staticmethod
    def __sort_if_range(values):
        if len(values) == 2 and None not in values:
            values.sort()
            return [f"{values[0]}/{values[1]}"]
        elif len(values) == 2:
            for value in values:
                if value is not None:
                    return [value]
        else:
            return values


class SubjectProperty(BaseProperty):
    # TODO: Should this even exist? Can't this just be BaseProperty?
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find_topic(self):
        subject_topic_value_uris = [uri for uri in self.root.xpath('mods:subject[mods:topic]/@valueURI', namespaces=self.namespaces)]
        topic_value_uris = [uri for uri in self.root.xpath('mods:subject/mods:topic/@valueURI', namespaces=self.namespaces)]
        subject_name_value_uris = [uri for uri in self.root.xpath('mods:subject[mods:name/mods:namePart]/@valueURI', namespaces=self.namespaces)]
        name_value_uris = [uri for uri in self.root.xpath('mods:subject/mods:name/@valueURI', namespaces=self.namespaces)]
        aat_genres = [uri for uri in self.root.xpath('mods:genre[@authority="aat"]/@valueURI', namespaces=self.namespaces)]
        lcmpt_genres = [uri for uri in self.root.xpath('mods:genre[@authority="lcmpt"]/@valueURI', namespaces=self.namespaces)]
        lcsh_genres = [uri for uri in self.root.xpath('mods:genre[@authority="lcsh"]/@valueURI', namespaces=self.namespaces)]
        all_initial_values = [subject_topic_value_uris, topic_value_uris, subject_name_value_uris, name_value_uris, aat_genres, lcmpt_genres, lcsh_genres]
        return_values = []
        for iterable in all_initial_values:
            for value in iterable:
                return_values.append(value)
        return {'subject': return_values}


class KeywordProperty(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find_topic(self):
        non_uris_topics = [value.text for value in self.root.xpath('mods:subject[not(@valueURI)]/mods:topic[not(@valueURI)]', namespaces=self.namespaces)]
        non_uris_names = [value.text for value in self.root.xpath('mods:subject[not(@valueURI)]/mods:name[not(@valueURI)]/mods:namePart[not(@valueURI)]', namespaces=self.namespaces)]
        all_initial_values = [non_uris_topics, non_uris_names]
        return_values = []
        for iterable in all_initial_values:
            for value in iterable:
                return_values.append(value)
        return {'keyword': return_values}


class TypesProperties(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find(self):
        return {
            'form': self.__find_edm_has_type(),
            'resource_type': self.__find_dcterms_type(),
            'form_local': self.__find_local_form()
        }

    def __find_dcterms_type(self):
        genre_uris = {
            "cartographic": "http://id.loc.gov/vocabulary/resourceTypes/car",
            "image": "http://id.loc.gov/vocabulary/resourceTypes/img",
            "notated music": "http://id.loc.gov/vocabulary/resourceTypes/not",
            "still image": "http://id.loc.gov/vocabulary/resourceTypes/img",
            "text": "http://id.loc.gov/vocabulary/resourceTypes/txt",
        }
        type_of_resource_uris = {
            "text": "http://id.loc.gov/vocabulary/resourceTypes/txt",
            "cartographic": "http://id.loc.gov/vocabulary/resourceTypes/car",
            "notated music": "http://id.loc.gov/vocabulary/resourceTypes/not",
            "sound recording-nonmusical": "http://id.loc.gov/vocabulary/resourceTypes/aun",
            "sound recording": "http://id.loc.gov/vocabulary/resourceTypes/aud",
            "still image": "http://id.loc.gov/vocabulary/resourceTypes/img",
            "moving image": "http://id.loc.gov/vocabulary/resourceTypes/mov",
            "three dimensional object": "http://id.loc.gov/vocabulary/resourceTypes/art",

        }
        # TODO: Works but messy!
        genre_to_dcterms_match_1 = [
            value.text
            for value in self.root.xpath(
                "mods:genre[not(@*)][string() = 'cartographic']",
                namespaces=self.namespaces
            )
        ]
        genre_to_dcterms_match_2 = [
            value.text
            for value in self.root.xpath(
                "mods:genre[not(@*)][string() = 'notated music']",
                namespaces=self.namespaces
            )
        ]
        genre_to_dcterms_match_3 = [
            value.text
            for value in self.root.xpath(
                "mods:genre[@authority = 'dct'][string() = 'image']",
                namespaces=self.namespaces
            )
        ]
        genre_to_dcterms_match_4 = [
            value.text
            for value in self.root.xpath(
                "mods:genre[@authority = 'dct'][string() = 'still image']",
                namespaces=self.namespaces
            )
        ]
        genre_to_dcterms_match_5 = [
            value.text
            for value in self.root.xpath(
                "mods:genre[@authority = 'dct'][string() = 'text']",
                namespaces=self.namespaces
            )
        ]
        genre_to_dcterms_matches = (genre_to_dcterms_match_1, genre_to_dcterms_match_2, genre_to_dcterms_match_3, genre_to_dcterms_match_4, genre_to_dcterms_match_5)
        type_of_resource_to_dcterms_type = [
            value.text
            for value in self.root.xpath(
                "mods:typeOfResource[not(@collection)]", namespaces=self.namespaces
            )
        ]
        type_of_resource_collection = [
            value.text
            for value in self.root.xpath(
                "mods:typeOfResource[@collection]", namespaces=self.namespaces
            )
        ]
        all_dcterms_types = []
        for matches in genre_to_dcterms_matches:
            for match in matches:
                if match in genre_uris:
                    all_dcterms_types.append(genre_uris[match])
        for value in type_of_resource_to_dcterms_type:
            if value in type_of_resource_uris:
                all_dcterms_types.append(type_of_resource_uris[value])

        if len(type_of_resource_collection) > 0:
            all_dcterms_types.append("http://id.loc.gov/vocabulary/resourceTypes/col")
        return all_dcterms_types

    def __find_edm_has_type(self):
        lcgft_genres = [uri for uri in self.root.xpath('mods:genre[@authority="lcgft"]/@valueURI', namespaces=self.namespaces)]
        form_uris = [uri for uri in self.root.xpath("mods:physicalDescription/mods:form/@valueURI", namespaces=self.namespaces)]
        all_matches = [lcgft_genres, form_uris]
        return_values = []
        for match in all_matches:
            for value in match:
                return_values.append(value)
        return return_values

    def __find_local_form(self):
        form_no_uri = [value.text for value in
                       self.root.xpath("mods:physicalDescription/mods:form[not(@valueURI)][not(@type='material')]",
                                       namespaces=self.namespaces)]
        genre_strings = [value.text for value in self.root.xpath(
            "mods:genre[not(@*) and not(text()='cartographic') and not(text()='notated music')]",
            namespaces=self.namespaces)]
        all_matches = [form_no_uri, genre_strings]
        return_values = []
        for match in all_matches:
            for value in match:
                return_values.append(value)
        return return_values


class LocalTypesProperties(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find(self):
        return {
            'resource_type_local': self.__find_dcterms_type(),
            'form_local': self.__find_local_form()
        }

    def __find_dcterms_type(self):
        genre_uris = {
            "cartographic": "http://id.loc.gov/vocabulary/resourceTypes/car",
            "image": "http://id.loc.gov/vocabulary/resourceTypes/img",
            "notated music": "http://id.loc.gov/vocabulary/resourceTypes/not",
            "still image": "http://id.loc.gov/vocabulary/resourceTypes/img",
            "text": "http://id.loc.gov/vocabulary/resourceTypes/txt",
        }
        type_of_resource_uris = {
            "text": "http://id.loc.gov/vocabulary/resourceTypes/txt",
            "cartographic": "http://id.loc.gov/vocabulary/resourceTypes/car",
            "notated music": "http://id.loc.gov/vocabulary/resourceTypes/not",
            "sound recording-nonmusical": "http://id.loc.gov/vocabulary/resourceTypes/aun",
            "sound recording": "http://id.loc.gov/vocabulary/resourceTypes/aud",
            "still image": "http://id.loc.gov/vocabulary/resourceTypes/img",
            "moving image": "http://id.loc.gov/vocabulary/resourceTypes/mov",
            "three dimensional object": "http://id.loc.gov/vocabulary/resourceTypes/art",

        }
        # TODO: Works but messy!
        genre_to_dcterms_match_1 = [
            value.text
            for value in self.root.xpath(
                "mods:genre[not(@*)][string() = 'cartographic']",
                namespaces=self.namespaces
            )
        ]
        genre_to_dcterms_match_2 = [
            value.text
            for value in self.root.xpath(
                "mods:genre[not(@*)][string() = 'notated music']",
                namespaces=self.namespaces
            )
        ]
        genre_to_dcterms_match_3 = [
            value.text
            for value in self.root.xpath(
                "mods:genre[@authority = 'dct'][string() = 'image']",
                namespaces=self.namespaces
            )
        ]
        genre_to_dcterms_match_4 = [
            value.text
            for value in self.root.xpath(
                "mods:genre[@authority = 'dct'][string() = 'still image']",
                namespaces=self.namespaces
            )
        ]
        genre_to_dcterms_match_5 = [
            value.text
            for value in self.root.xpath(
                "mods:genre[@authority = 'dct'][string() = 'text']",
                namespaces=self.namespaces
            )
        ]
        genre_to_dcterms_matches = (genre_to_dcterms_match_1, genre_to_dcterms_match_2, genre_to_dcterms_match_3, genre_to_dcterms_match_4, genre_to_dcterms_match_5)
        type_of_resource_to_dcterms_type = [
            value.text
            for value in self.root.xpath(
                "mods:typeOfResource[not(@collection)]", namespaces=self.namespaces
            )
        ]
        type_of_resource_collection = [
            value.text
            for value in self.root.xpath(
                "mods:typeOfResource[@collection]", namespaces=self.namespaces
            )
        ]
        all_dcterms_types = []
        for matches in genre_to_dcterms_matches:
            for match in matches:
                if match in genre_uris:
                    all_dcterms_types.append(match)
        for value in type_of_resource_to_dcterms_type:
            if value in type_of_resource_uris:
                all_dcterms_types.append(value)

        if len(type_of_resource_collection) > 0:
            all_dcterms_types.append("http://id.loc.gov/vocabulary/resourceTypes/col")
        return all_dcterms_types

    def __find_local_form(self):
        form_no_uri = [value.text for value in
                       self.root.xpath("mods:physicalDescription/mods:form[not(@type='material')]",
                                       namespaces=self.namespaces)]
        genre_strings = [value.text for value in self.root.xpath(
            "mods:genre[not(text()='cartographic') and not(text()='notated music')]",
            namespaces=self.namespaces)]
        all_matches = [form_no_uri, genre_strings]
        return_values = []
        for match in all_matches:
            for value in match:
                return_values.append(value)
        return return_values


class PublisherProperty(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find(self):
        return {"publisher": [uri for uri in self.root.xpath('mods:originInfo/mods:publisher/@valueURI', namespaces=self.namespaces)]}


class RightsOrLicenseProperties(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find(self):
        final = {}
        rights = [uri for uri in self.root.xpath('mods:accessCondition[not(@type="restriction on access")]/@xlink:href', namespaces=self.namespaces) if "rightsstatements.org" in uri]
        licenses = [uri.replace('https://', 'http://') for uri in self.root.xpath('mods:accessCondition[not(@type="restriction on access")]/@xlink:href', namespaces=self.namespaces) if "creativecommons.org" in uri]
        if len(rights) > 0:
            final['rights_statement'] = rights
        if len(licenses) > 0:
            final['license'] = licenses
        if len(rights) == 0:
            if licenses[0] == 'http://creativecommons.org/publicdomain/zero/1.0/':
                final['rights_statement'] = ['http://rightsstatements.org/vocab/NKC/1.0/']
            else:
                final['rights_statement'] = ['http://rightsstatements.org/vocab/InC/1.0/']
        return final


class PublicationPlaceProperty(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find(self):
        return {"publication_place": [uri for uri in self.root.xpath('mods:originInfo/mods:place/mods:placeTerm/@valueURI', namespaces=self.namespaces)]}


class LanguageURIProperty(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find_term(self):
        terms_and_uris = {
            "English": "http://id.loc.gov/vocabulary/iso639-2/eng",
            "French": "http://id.loc.gov/vocabulary/iso639-2/fre",
            "German": "http://id.loc.gov/vocabulary/iso639-2/ger",
            "Italian": "http://id.loc.gov/vocabulary/iso639-2/ita",
            "Latin": "http://id.loc.gov/vocabulary/iso639-2/lat",
            "No linguistic content": "http://id.loc.gov/vocabulary/iso639-2/zxx",
            "Russian": "http://id.loc.gov/vocabulary/iso639-2/rus",
            "Spanish": "http://id.loc.gov/vocabulary/iso639-2/spa",
            "Swedish": "http://id.loc.gov/vocabulary/iso639-2/swe",
            "en": "http://id.loc.gov/vocabulary/iso639-2/eng",
        }
        language_terms = [
            value.text
            for value in self.root.xpath(
                "mods:language/mods:languageTerm", namespaces=self.namespaces
            )
        ]
        lanuage_uris = []
        for language in language_terms:
            if language in terms_and_uris:
                lanuage_uris.append(terms_and_uris[language])
        return {"language": lanuage_uris}


class ExtentProperty(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find(self):
        no_units = [text.text for text in self.root.xpath('mods:physicalDescription/mods:extent[not(@unit)]', namespaces=self.namespaces)]
        with_units = [node for node in self.root.xpath('mods:physicalDescription/mods:extent[@unit]', namespaces=self.namespaces)]
        final_extent = []
        if len(with_units) > 0:
            for unit in with_units:
                final_extent.append(f"{unit.text} {unit.attrib['unit']}")
        for unit in no_units:
            final_extent.append(unit)
        return {"extent": final_extent}


class MetadataMapping:
    def __init__(self, path_to_mapping, file_path, membership_details=None):
        self.path = path_to_mapping
        self.membership_details = membership_details
        self.fieldnames = []
        self.all_files = self.__get_all_files(file_path)
        self.mapping_data = yaml.safe_load(open(path_to_mapping, "r"))['mapping']
        self.namespaces = {"mods": "http://www.loc.gov/mods/v3", "xlink": "http://www.w3.org/1999/xlink"}
        self.output_data = self.__execute(self.namespaces)

    @staticmethod
    def __get_all_files(path):
        all_files = []
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                all_files.append(os.path.join(root, name))
        return all_files

    def __execute(self, namespaces):
        all_file_data = []
        for file in tqdm(self.all_files):
            # TODO: Ultimately, parents should be populated based on relationship.
            model = self.__dereference_islandora_type(file)
            output_data = {
                'source_identifier': file.split('/')[-1].replace('_MODS.xml', '').replace('.xml', ''),
                'model': model,
                'remote_files': '',
                'parents': ' | '.join(ResourceIndexSearch().get_parent_collections(file.split('/')[-1].replace('_MODS.xml', '').replace('.xml', '')),),
                'has_work_type': self.__get_utk_ontology_value(model),
                'primary_identifier': file.split('/')[-1].replace('_MODS.xml', '').replace('.xml', ''),
            }
            self.__dereference_islandora_type(file)
            for rdf_property in self.mapping_data:
                if 'special' not in rdf_property:
                    final_values = ""
                    values = StandardProperty(file, namespaces).find(rdf_property['xpaths'])
                    if len(values) > 0:
                        # TODO: Make delimeter configurable
                        final_values = ' | '.join(values)
                    output_data[rdf_property['name']] = final_values
                else:
                    special = self.__lookup_special_property(
                        rdf_property['special'], file, namespaces, rdf_property['name']
                    )
                    for k, v in special.items():
                        # TODO: Make delimeter configurable
                        if v != [[]]:
                            try:
                                output_data[k] = ' | '.join(v)
                            except TypeError:
                                print(f"{TypeError}: {file}")
            self.__find_unique_fieldnames(output_data)
            all_file_data.append(output_data)
        return all_file_data

    def __find_unique_fieldnames(self, data):
        for k, v in data.items():
            if k not in self.fieldnames:
                self.fieldnames.append(k)
        return

    def __dereference_islandora_type(self, file):
        islandora_types = {
            "info:fedora/islandora:sp-audioCModel": "Audio",
            "info:fedora/islandora:bookCModel": "Book",
            "info:fedora/islandora:binaryObjectCModel": "Generic",
            "info:fedora/islandora:sp_large_image_cmodel": "Image",
            "info:fedora/islandora:sp_basic_image": "Image",
            "info:fedora/islandora:sp_pdf": "Pdf",
            "info:fedora/islandora:sp_videoCModel": "Video",
        }
        x = ResourceIndexSearch().get_islandora_work_type(file.split('/')[-1].replace('_MODS.xml', '').replace('.xml', ''))
        return islandora_types[x]

    def __get_utk_ontology_value(self, model):
        ontology_values ={
            "Audio": "https://ontology.lib.utk.edu/works#AudioWork",
            "Book": "https://ontology.lib.utk.edu/works#BookWork",
            "Generic": "https://ontology.lib.utk.edu/works#GenericWork",
            "Image": "https://ontology.lib.utk.edu/works#ImageWork",
            "Pdf": "https://ontology.lib.utk.edu/works#PDFWork",
            "Video": "https://ontology.lib.utk.edu/works#VideoWork",
        }
        return ontology_values[model]

    @staticmethod
    def __lookup_special_property(special_property, file, namespaces, name):
        match special_property:
            case "TitleProperty":
                return TitleProperty(file, namespaces).find()
            case "NameProperty":
                return NameProperty(file).find()
            case "RoleAndNameProperty":
                return RoleAndNameProperty(file).find()
            case "GeoNamesProperty":
                return GeoNamesProperty(file, namespaces).find(name)
            case "DataProvider":
                return DataProvider(file, namespaces).find()
            case "PhysicalLocationsProperties":
                return PhysicalLocationsProperties(file, namespaces).find()
            case "SubjectProperty":
                return SubjectProperty(file, namespaces).find_topic()
            case "KeywordProperty":
                return KeywordProperty(file, namespaces).find_topic()
            case "TypesProperties":
                return TypesProperties(file, namespaces).find()
            case "LocalTypesProperties":
                return LocalTypesProperties(file, namespaces).find()
            case "LanguageURIProperty":
                return LanguageURIProperty(file, namespaces).find_term()
            case "PublisherProperty":
                return PublisherProperty(file, namespaces).find()
            case "PublicationPlaceProperty":
                return PublicationPlaceProperty(file, namespaces).find()
            case "RightsOrLicenseProperties":
                return RightsOrLicenseProperties(file, namespaces).find()
            case "ExtentProperty":
                return ExtentProperty(file, namespaces).find()
            case "MachineDate":
                return MachineDate(file, namespaces).find()

    def write_csv(self, filename):
        with open(filename, 'w', newline='') as bulkrax_sheet:
            writer = csv.DictWriter(bulkrax_sheet, fieldnames=self.fieldnames)
            writer.writeheader()
            for data in self.output_data:
                writer.writerow(data)
        return


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Build migration works sheet.')
    parser.add_argument("-s", "--sheet", dest="sheet", help="Specify csv to test.", required=True)
    parser.add_argument("-c", "--config", dest="config", help="Specify a config.", default="configs/utk_dc.yml")
    parser.add_argument("-p", "--path", dest="path_to_files", help="Specify path to metadata files.", required=True)
    args = parser.parse_args()
    test = MetadataMapping(
        args.config,
        args.path_to_files
    )
    test.write_csv(
        args.sheet
    )
