Deleting FileSets and Works
###########################

Sometimes, things go wrong and you need to remove a work or filesets and their attached files from the repository. This
section covers when to do it and how to do it.

Identifying Failed Filesets and Works
=====================================

The Bulkrax importer page in a Hyku instance does not necessarily return all works and filesets. Instead, it grabs a set
of files and displays them to the page but does so without understanding what works and filesets appear on the previous
or subsequent pages.

In order to determine what in an importer failed, we need to export errored entries. To do this, visit the importer page
and append :code:`/export_errors` like this `https://dc.utk-hyku-staging.notch8.cloud/importers/141/export_errors <https://dc.utk-hyku-staging.notch8.cloud/importers/141/export_errors>`_.

When To Delete
==============

How To Delete
=============
