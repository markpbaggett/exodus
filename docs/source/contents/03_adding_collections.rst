Adding Collections and Collection Metadata
##########################################

Collection metadata is also done separately and can occur anytime. This is because it is assumed you don't always want
to add or update metadata about a collection.

In order to add collections to an importer, you can use the :code:`get_collection_data.py` helper. This script crawls a
CSV, finds which collections the work currently belongs to, adds the relationships via the parents column, and then adds
a row for each collection found in this process.

Note that collection metadata for this process is prescribed in the script. At the time of this writing, only these elements
are captured from the MODS record of the collection:

.. code-block:: python

    def grab_all_metadata(self):
        return {
            "source_identifier": self.pid,
            "model": "Collection",
            "parents": "",
            "title": self.__simplify_xpath('mods:titleInfo/mods:title'),
            "abstract": self.__simplify_xpath('mods:abstract'),
            "contributor": "",
            "utk_contributor": "",
            "creator": self.__get_valueURIs('mods:name/@valueURI'),
            "utk_creator": self.__simplify_xpath('mods:name[not(@valueURI)]/mods:namePart'),
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

In order to add collection metadata and relationships to an importer, you can run this where :code:`-s` is your sheet
with the works and :code:`-c` is the new sheet.

.. code-block:: shell

    python exodus/helpers/get_collection_data.py -s roth.csv -c roth_with_collections.csv

In our migration workflow, we currently create the initial importer to include only collections and works (no filesets
or attachments).
