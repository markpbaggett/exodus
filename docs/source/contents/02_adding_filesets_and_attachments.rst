Adding Filesets and Attachments
###############################

Adding filesets and attachments is handled in separately in this repository. This is because it is a common use case to
want to be able to generate an importer without filesets. An examples use case is metadata cleanup. You may want to do
metadata cleanup in a separate application such as OpenRefine. To make this use case as easy as possible, we add filesets
and attachments in a separate process.

If you want to add filesets and attachments to a sheet, you can do so by making use of the organizer package. This package
has a class called :code:`FileOrganizer` that reads in a csv with works, coverts it to a :code:`dict`, and grabs the
headings for the incoming csv. For each work in the csv, a call to the resource index is performed to figure out the datastreams
that exist for it in our current repository. It then decides whether or not that datastream is important by following
the `prescribed google sheet <https://docs.google.com/spreadsheets/d/1sNFvt7T2kQ3Y6b97iG-W8spiyOyNXVhGSz38VhAqUNw/edit#gid=353466099>`_.

If the data stream is important, an :code:`Attachment` and :code:`Filesheet` are added to the importer. It is assumed that
the path to the fileset should match what it is now. This can be modified when needed by following a separate process.

In order to add :code:`Attachments` and :code:`Filesets`, you can run something like this with the path to the importer
with works and an output path.

.. code-block:: shell

    python organizer/organizer.py -s roth.csv -f roth_with_files.csv

Curating FileSets and Attachments
=================================

Sometimes, you may need to create an importer with just the FileSets and Attachments -- no works or collections or take
an importer with just filesets and attachments and split it into separate import. The :code:`curate_for_filesets_attachments.py`
helper can handle this. This helper allows you to build an importer that has all filesheets and attachments in a sheet
or split all the filesets and attachments into multiple sheets.

If you wanted to generate a sheets of 3000 items (1500 attachments / 1500 filesets) from an import sheet, you could use
the script like this:

.. code-block:: shell

    python exodus/helpers/find_and_fix_private_works.py -s roth_with_filesets_and_attachments.csv -t 3000 -f roth_just_filesets_and_attachments.csv

This would generate sheets in this pattern:  :code:`roth_just_filesets_and_attachments{n}.csv`




