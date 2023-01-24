Validating Import Sheets
########################

It is a good idea to always validate import sheets that include anything mentioned in the m3 profile (a work like Image
or an Attachment) to ensure the expectations of the profile are in line. Failure to do so can  lead to import jobs failing
to run properly.

A validation helper is included to aid in this process. The validator crawls a spreadsheet and checks that the item in
current row has a valid model, that the values of each metadata field meet the cardinality and range requirements described
in the m3 profile, that a license is valid if a license is present, and that all required fields in the m3 profile per work
type are present.  Once the validator is done running, it will print all exceptions it found and allow you to fix those
before import. Keep in mind that this does not check rows for collections or filesets.

To run the validator, you can run this script:

.. code-block:: python

    python exodus/validation/validation.py -s roth.csv
