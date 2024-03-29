Philosophy, Patterns, and Strategy
##################################

Migrating from one system to another is hard work. It requires understanding the data model of the new and previous
system and the various tooling of both systems. In order to migrate content into Hyku, we were instructed by our vendor
to use a tool called `Bulkrax <https://github.com/samvera-labs/bulkrax>`_.

This document describes Bulkrax, how we use it, and how we massage our data to fit the shape it expects.

What is Bulkrax
===============

`Bulkrax <https://github.com/samvera-labs/bulkrax>`_ is a batteries included importer for Hyrax-based repositories. It
currently includes support for OAI-PMH (DC and Qualified DC) and CSV out of the box. It is also designed to be
extensible, allowing you to easily add new importers in to your application or to include them with other gems. Bulkrax
provides a full admin interface including creating, editing, scheduling,and reviewing imports.

Documentation about Bulkrax can be found in its `wiki <https://github.com/samvera-labs/bulkrax/wiki>`_.

UTK Procedures for Bulkrax Imports
==================================

UTK has a rather complex data model in its Hyku instance.  In this model, Works have Attachments, Attachments have
FileSets, and FileSets have Files. While we don't love this model, it is what Softserve said needed to happen to be able
to support our use of :code:`pcdmuse:PreservationFile` and :code:`pcdmuse:IntermediateFile`.

When creating a Bulkrax import, it's important to know that Collections can have Collections or Works, Works can have
Attachments, and Attachments should have Filesets. Importers should follow this model. Even though the Bulkrax documentation
in the wiki shows different variations of data models, our data should follow thing one.

While Bulkrax supports multiple import methods, UTK uses CSV only.

##########
Delimiting
##########

While there may be several supported patterns, UTK separates values with this delmiter only:  :code:` | `.

######################
Required System Fields
######################

CSV imports have a few required fields.

:code:`source_identifier` is the required identifier that is human readable and aligns with a Hyrax assigned UUID later.
This identifier must be unique. For migration, we follow this pattern: :code:`{namespace}:{id}_{dsid}_{utk_hyku_type}`.
In other words, if you are referencing an image work whose Islandora 7 PID is :code:`archivision:6910`, its
:code:`source_identifier` would be :code:`archivision:6910`. If you are referencing the :code:`OBJ` datastream for
:code:`archivision:6910` there are 2 patterns. The parent attachment would be :code:`archivision:6910_OBJ_attachment`
while the fileset would be :code:`archivision:6910_OBJ_fileset`. When you run your import, only the fileset will have
information about the actual file.

The second required property is :code:`model`. This field contains the work type of the item described in the row or
:code:`Collection`, :code:`FileSet`, or :code:`Attachment`.

###################
Other System Fields
###################

There are a few other fields prescribed by Bulkrax that are optional.

:code:`remote_files` is used by :code:`FileSet`s to store the file's location. Only use this for file sets.

Relationships can be stated with :code:`parents`. The values here if the column is included should reference the parents
of the item in the row.  If the column is here and the field is blank, all existing relationships will be removed.
Since this is the case, always remove the column unless you are stating a new relationship. If you leave this here and the
relationship already exists, the create relationships job will still run which will slow down processing. In other words,
only use when you need.

Visibility can be specified with :code:`visibility`. If present and blank, the work defaults to public.  Institution only
should be :code:`authenticated` while private should be :code:`private`.

The :code:`delete` field can be used to delete something. To remove the thing in the row, simple add :code:`TRUE` to the
field.

##########
UTK Fields
##########

Fields defined by UTK are prescribed in our `m3 profile <https://github.com/utkdigitalinitiatives/m3_profiles/blob/main/maps/utk.yml>`_.
Each property and the classes where they can appear are described here.

The exception to this is collections.  Collections are defined in our app as
`decorators <https://github.com/scientist-softserv/utk-hyku/blob/8a980acf9228291ef213247e5f1462527699061c/app/forms/hyrax/forms/collection_form_decorator.rb>`_.

Migration Philosophy
====================

UTK's philosophy for migration is to automate as much of the migration as possible without touching metadata or files by
hand. In order to prepare for migration, UTK developed a `metadata mapping <https://utk-mods-to-rdf.readthedocs.io/>`_
from MODS to RDF that informs migration utilities how to read in descriptive metadata in MODS and write it to the correct
RDF field.

In order to align code with this metadata mapping, UTK starts by defining a machine-readable config for working with its
descriptive metadata. The machine readable file is in yaml. The yaml file has 1 property called :code:`mapping` with an
array of properties that align with our m3 profile or another m3 profile.

There are two patterns for properties:  :code:`basic` and :code:`special`.

A :code:`basic` property is used for straight foward metadata components where logic can be handled with basic XPATH.
The anatomy of a :code:`basic` property has 3 properties (2 of which are used). These three properties are :code:`name`,
:code:`xpath`, and :code:`property`. The :code:`name` property stores which column in the spreadsheet a field should be
written to and should align with our m3 profile. The :code:`xpaths` property is an array and should have all xpaths in
which to pull values from. The :code:`property` property is not actually used, but included to make derferencing between
the m3 profile and config easier.

A basic property may look like this:

.. code-block:: yaml

      - name: date_other
        xpaths:
          - 'mods:originInfo/mods:dateOther[not(@encoding="edtf")]'
        property: "http://purl.org/dc/terms/date"

A :code:`special` property is used when you have complex scenarios to determine which field the value of an xpath should
be written to. A :code:`special` property may align with 1 or more properties in an m3 profile. In the config, a
:code:`special` property should have 4 properties.  The most critical property is :code:`special`. This property specifies
the name of the class in our code base that aligns with the concept here.  The other 3 properties are not used in code,
but help us understand what the code is doing from the config. :code:`name` contains the concept or concepts that this
covers. If it aligns directly with the m3 profile, it should use the same value.  The :code:`xpaths` property includes
all xpaths that apply here.  Finally, the :code:`properties` property describes which properties in the m3 profiles this
concept relates to.

A special property may look like this:

.. code-block:: yaml

      - name: machine_date
        xpaths:
          - 'mods:originInfo/mods:dateOther[@encoding="edtf"]'
          - 'mods:originInfo/mods:dateCreated[@encoding="edtf"]'
          - 'mods:originInfo/mods:dateIssued[@encoding="edtf"]'
        properties:
          - "https://dbpedia.org/ontology/date"
          - "https://dbpedia.org/ontology/publicationDate"
          - "https://dbpedia.org/ontology/completionDate"
        special: MachineDate

The properties listed in the yaml closely correlate to code found in this repository.  A :code:`basic` property aligns
with the :code:`StandardProperty` class found `here <https://github.com/markpbaggett/exodus/blob/main/exodus/exodus.py#L18>`_.
Note that code here only allows a standard XPATH for an attribute if it is specified.  This should be improved:

.. code-block:: python

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

All :code:`special` properties align with the class that is listed in their :code:`special` property in the yaml. For
instance, :code:`titleInfo` expectations are expressed `here <https://utk-mods-to-rdf.readthedocs.io/en/latest/contents/4_mapping.html#titleinfo>`_.
Note that a text node in just :code:`mods:titleInfo/mods:title` or :code:`titleInfo[@supplied="yes"]/title` should be
mapped to :code:`dcterms:title`, but if both :code:`mods:titleInfo/mods:title` and :code:`titleInfo[@supplied="yes"]/title`
exist, the former should be mapped to :code:`dcterms:title` and the latter to :code:`dcterms:alternative`. Because the
logic here is difficult to express in basic XPATH, special classes are defined and utilized.

.. code-block:: python

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