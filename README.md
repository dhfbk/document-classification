# Document classification utils

This project contains some useful tools for various document classification tasks. More specifically ...


## Running from Docker

To run the project as a Docker container you first need to prepare the required data. In particular, prepare a folder that contains
* ``models`` folder with the model files
* ``label_mappings`` folder including the JSON files (one per language, `it.json` for Italian)
  containing the descriptions of the EuroVoc labels
* ``id2label.json`` JSON file containing the descriptions of the IPZS
* ``i2eu_id.json`` JSON file containing the mappings between IPZS and EuroVoc codes
  
To execute the docker container, run the following command:
```
docker run -p 80:80 -v /path/to/data/folder:/data/ smartcommunitylab/document-classification
```
where ``/path/to/data/folder`` should refer to the folder with the above data.

Once started (may require quite some time due to the size of image and the models), it is possible to 
* use Web interface available on ``http://localhost/ui``
* consult the API documentation of the server ``http://localhost/redoc``

## Creating Docker image
To create a new version of the Docker image, run the following command from this directory
```
docker build -t imagename
```
replacing ``imagename`` with the name of your choice.



