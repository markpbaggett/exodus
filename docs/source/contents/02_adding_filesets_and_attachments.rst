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
