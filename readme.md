# elasticsearch-api

A collection of RESTful API's, written and tested using the `Flask` framework of `Python` language, for interacting with the `Elastic-cluster` without breaking any security protocol or exposing any credentials/access tokens/confidential data.

## Currently Supports

1. Index creation:
    - - [x] Creating Indices.
    - - [x] Assigning ID-s.
    - - [x] Timestamp is mandatory in the records that are being indexed.
  
2. Functionality to load the data in the system:
    - - [x] Bulk indexing the data (from file).
    - - [x] File should be of `csv` or `json` type.
    - - [x] Inserting a single document.

3. Functionality to search the data:
    - - [x] Search on the basis of unique id.
    - - [x] Search on the basis of any specific key value.
    - - [x] Search and fetch the records in the time range given as input.
    - - [x] Keyword-based search functionality.
    - - [x] Full-text search functionality.
  
4. Aggregated info of my data.
    - - [ ] Create `Kibana` dashboard for the data that is inserted
    - - [ ] Visualize and analyze the data from dashboard.


<br>

## Instructions to setup and run the application locally

- `python --version` should be `>=3` and `<=3.10`

<br>

**Star and Fork** the repository. Download or clone

    # clone the repository
    $ git clone https://github.com/atanughosh01/elasticsearch-api
    $ cd elasticsearch-api

Create a virtualenv and activate it

    $ python3 -m venv venv
    $ . venv/bin/activate

Or on Windows cmd

    $ py -3 -m venv venv
    $ venv\Scripts\activate.bat

Or on Windows powershell

    $ python3 -m venv venv
    $ & venv\Scripts\Activate.ps1

Install pip requirements

    $ pip install -U -r requirements.txt


### Run the application

    $ export FLASK_APP=api
    $ export FLASK_ENV=development
    $ flask run

Or on Windows cmd

    > set -x FLASK_APP=api
    > set -x FLASK_ENV=development
    > flask run

Or on Windows powershell

    > $env:FLASK_APP = "api"
    > $env:FLASK_ENV = "development"
    > flask run

### Alternate way to run the application

Create a `.flaskenv` in the `root` directory with the following content

    export FLASK_APP=api
    export FLASK_ENV=development

Make sure that `python-dotenv` is installed
    
    $ pip install python-dotenv==0.20.0

Then execute `flask run` on the terminal.

<br>

Open `http://127.0.0.1:5000` in a browser.\
Use **Postman** to test the collection of API's.


<br>

## Steps for Containerization

- Move to the `root` directory.
- Check if the `.flaskenv` file exists, if not create it
- Make sure whether `Docker` is running or not

        $ docker version
        $ docker images

- Build the docker image with `Dockerfile`

        $ docker build -t es-api:v0.0.1 .

- Run the docker image

        $ docker run --name ElasticAPI -p 5000:5000 -d es-api:v0.0.1

- Check the status of the container

        $ docker ps

<br>

Open `localhost:5000` in a browser.\
Use **Postman** to test the collection of API's.


<!-- Dockerfile

    FROM python:3.9-alpine
    RUN apk add --no-cache python3-pip
    RUN pip3 install -r requirements.txt
    WORKDIR /app
    COPY . .
    EXPOSE 5000
    CMD ["python", "app.py"] -->
