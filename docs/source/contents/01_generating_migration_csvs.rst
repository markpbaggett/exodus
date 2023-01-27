Generating Migration CSVs for Works
###################################

Currently, migration spreadsheets need to be generated on a per work type basis. This is due to a few factors including
that we still do not know how we are going to migrate :code:`books` and :code:`compound objects`. This factor thus
requires one to download the metadata that they want to generate a Bulkrax importer for.

Identifying and Downloading Metadata
====================================

In order to get metadata, your best source IMHO is the `Fedora resource index <https://porter.lib.utk.edu/fedora/risearch>`_.
Using the resource index, we can be very opinionated about what things to include in our set and what not.  This is due
to the amount of data the resource index includes about each object. While there is arguably more data available via the
API, each call requires at least one HTTP request. With the resource index, we can get back many results with just one
request.

One of the most difficult sets of data to narrow down is images.  This is because an image can stand on its own or be a
part of another work (compound objects). While its very difficult to get the images you want with just the resource index,
we can add in a touch of scripting to get exactly what we want. If we wanted to get a list of all large images from a
particular collection (let's say gsmrc:roth), we could write a sparql query like this:

.. code-block:: sparql

    SELECT ?pid FROM <#ri> WHERE {
        ?pid <info:fedora/fedora-system:def/model#hasModel> <info:fedora/islandora:sp_large_image_cmodel> ;
        <info:fedora/fedora-system:def/relations-external#isMemberOfCollection> <info:fedora/gsmrc:roth> .
    }

This query is good, but it's dangerous. This is because the query could return large images that are a part of other
compound objects. If we wanted to get a list of images from roth that were a part of a compound object, we could write a
query like this.

.. code-block:: sparql

    SELECT ?pid FROM <#ri> WHERE {
        ?pid <info:fedora/fedora-system:def/model#hasModel> <info:fedora/islandora:sp_large_image_cmodel> ;
        <info:fedora/fedora-system:def/relations-external#isMemberOfCollection> <info:fedora/gsmrc:roth> ;
        <info:fedora/fedora-system:def/relations-external#isConstituentOf> ?unknown. }
    }

With your results set for both of these queries, one could then build an array that stores items all the large images
and the large images that are part of the compound object. Then, diffing the two can remove the parts.

This convoluted but rather simple process informs how we mainly do identification. While we use Sparql, we do it with
Python so we can use literal string interpolation.

.. code-block:: python

    def get_images_no_parts(self, collection):
        members_of_collection_query = self.escape_query(
            f"""SELECT ?pid FROM <#ri> WHERE {{ ?pid <info:fedora/fedora-system:def/model#hasModel> <info:fedora/islandora:sp_large_image_cmodel> ; <info:fedora/fedora-system:def/relations-external#isMemberOfCollection> <info:fedora/{collection}> . }}"""
        )
        members_of_collection_parts_query = self.escape_query(
            f"""SELECT ?pid FROM <#ri> WHERE {{ ?pid <info:fedora/fedora-system:def/model#hasModel> <info:fedora/islandora:sp_large_image_cmodel> ; <info:fedora/fedora-system:def/relations-external#isMemberOfCollection> <info:fedora/{collection}> ; <info:fedora/fedora-system:def/relations-external#isConstituentOf> ?unknown. }}"""
        )
        members_of_collection = self.__request_pids(members_of_collection_query)
        members_of_collection_parts = self.__request_pids(members_of_collection_parts_query)
        members_of_collection_no_parts = [pid for pid in members_of_collection if pid not in members_of_collection_parts]
        return members_of_collection_no_parts

An easy to use script with arg parsing is included:

.. code-block:: shell

    python exodus/helpers/risearch.py -c "gsmrc:roth" -o roth.txt

Using the contents of the output of the above text file, you can now use the API to get the metadata you need to build
an import sheet. One approach with Python could be to run a script like this against the file:

.. code-block:: python

    import requests

    class FedoraObject:
        def __init__(self, auth, fedora_uri):
            self.auth = auth
            self.fedora_uri = fedora_uri

        def getDatastream(self, pid, dsid, output):
            mimetypes = {
                'image/tiff': 'tif',
                'image/jp2': 'jp2',
                'application/xml': 'xml'
            }
            r = requests.get(f"{self.fedora_uri}/objects/{pid}/datastreams/{dsid}/content", auth=self.auth, allow_redirects=True)
            if r.status_code == 200:
                open(f'{output}/{pid}.{mimetypes[r.headers["Content-Type"]]}', 'wb').write(r.content)
            else:
                print(f'{r.status_code} on {pid}.')


    with open('roth.txt', 'r') as my_list:
        for line in my_list:
            x = FedoraObject(auth=("username", "password"), fedora_uri='http://localhost:8080/fedora')
            x.getDatastream(pid=f"{line.replace('info:fedora/','').strip()}", dsid='MODS', output='roth_mods')

Generating an Importer with Metadata
====================================

Once you have metadata, you can generate a fresh importer with :code:`exodus/exodus.py`. This assumes that you've
defined a config and any special classes to work with complex fields.

To generate the importer, one could run the code below by pointing at the path to the mods in question, adding where you want
to write your importer csv, and declaring with config to pull your rules from:

.. code-block:: shell

    python exodus/exodus.py -s roth.csv -p roth_mods -c configs/utk_dc.yml

