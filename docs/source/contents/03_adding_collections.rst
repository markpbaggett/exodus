Adding Collections and Collection Metadata
##########################################

Collection metadata is also done separately and can occur anytime. This is because it is assumed you don't always want
to add or update metadata about a collection.

In order to add collections to an importer, you can use the :code:`get_collection_data.py` helper. This script crawls a
CSV, finds which collections the work currently belongs to, adds the relationships via the parents column, and then adds
a row for each collection found in this process.

Note that collection metadata for this process is prescribed in the script. At the time of this writing, only these elements
are captured from the MODS record of the collection:

.. literalinclude:: ../../../exodus/helpers/get_collection_data.py
    :start-at: def grab_all_metadata(self):
    :end-at: }

In order to add collection metadata and relationships to an importer, you can run this where :code:`-s` is your sheet
with the works and :code:`-c` is the new sheet.

.. code-block:: shell

    python exodus/helpers/get_collection_data.py -s roth.csv -c roth_with_collections.csv

In our migration workflow, we currently create the initial importer to include only collections and works (no filesets
or attachments).
