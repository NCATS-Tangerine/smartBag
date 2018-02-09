# smartBag

## Context

The emerging ecosystem of complementary conventions for archiving data sets is colliding, in a good way, with innovations in semantic annotation for federated web APIs. smartBag blends these with a view to making semantically rich, machine readable data the norm.

### Data Archiving Conventions

The [NIH Data Commons](https://commonfund.nih.gov/bd2k/commons) seeks to create a unified platform for biomedial computing. It makes use of a number of data protocols including:

* **[Bagit](https://en.wikipedia.org/wiki/BagIt)** is a file packaging protocol.
* **[Bagit-RO](https://github.com/ResearchObject/bagit-ro)** integrates the Bagit and [Research Object](http://www.researchobject.org/) frameworks.
* **[BDBags](http://bd2k.ini.usc.edu/tools/bdbag/)** extends Bagit-RO so that referenced data files may be remote, referenced via ids with checksums.

### Semantic Annotation for Web APIs

The [NCATS Data Translator](https://ncats.nih.gov/translator) is annotating federated web APIs with semantic information. This makes biomedical data amenable to automated discovery, access, and reasoning.

* **[RDF](https://www.w3.org/RDF/)** Is a knowledge representation format.
* **[JSON](https://www.json.org/)** Is a data serialization format widely used on the web.
* **[OpenAPI](https://en.wikipedia.org/wiki/OpenAPI_Specification)** Is a specification for describing web data interfaces.
* **[smartAPI](http://smart-api.info/)** Extends the OpenAPI spec with additional metadata.
* **[JSON-LD](https://json-ld.org/)** Is an RDF serialization format for JSON.

## Challenge

**Translator** is making automated reasoning over biomedical data tractable but is gated by

* **Development**: Exposing data as web APIs is tedious and expensive.
* **Technology**: The underlying technologies to do this are in perpetual flux.

The **Data Commons** is providing scalable computing and a home for large biomedical data but would benefit from

* **Semantic Annotation**: A base line approach for publishing data sets for dynamic query with semantic metadata.
* **Support for AI**: Methods for data stewards to make data amenable to automated resoning. 

## Make it Go

It would be better to

  * **Annotate**: Annotate data archives with appropriate semantic and ontological metadata.
  * **Generate**: Compile the data and semantics to publish them into various evolving tech pipelines.

### Annotate

The smartBag tool chain lets data stewards (optimally) or consumers (pragmatically) semantically annotate their data sources using Research Object (RO) conventions. Use JSON-LD contexts to specify the identifiers and ontologies describing tabular data. smartBag integrates the Bagit suite of conventions with the [Data Translator](https://ncats.nih.gov/translator).

### Generate

The smartBag toolchain will generate an executable smartAPI from a properly annotated bag. Data stewards who annotate their data will be rewarded with the flexibility to compile data publishing pipelines to target arbitrary data delivery and execution platforms.

## Getting Started

In the following steps we use the example/ctd directory to compile a smartAPI for accessing a subset of the Clinical Toxicogenomic Database.

### Clone

These steps clone the repo and set up your path to use the toolchain:

```
git clone git@github.com:NCATS-Tangerine/smartBag.git
cd smartBag
pip install -r requirements.txt
export PATH=$PWD/bin:$PATH
```

### Configure

Next, we download data files for the data set we're working with. In this case, they're for CTD. The metadata frame of the bag is in the example/ctd directory and is structured like this:
```
└── metadata
    ├── annotations
    │   ├── CTD_chem_gene_ixn_types.csv.jsonld
    │   ├── CTD_chemicals.csv.jsonld
    │   └── CTD_pathways.csv.jsonld
    ├── manifest.json
    └── provenance
        └── results.prov.jsonld
```
This step also configures the bag we'll create by copying JSON-LD and other metadata as well as data files into a bag staging directory.
```
cd example/ctd
./configure
```

This stages a bag directory structure blending selected data files with metadata like this:
```
├── CTD_chem_gene_ixn_types.csv
├── CTD_chemicals.csv
├── CTD_pathways.csv
└── metadata
    ├── annotations
    │   ├── CTD_chem_gene_ixn_types.csv.jsonld
    │   ├── CTD_chemicals.csv.jsonld
    │   └── CTD_pathways.csv.jsonld
    ├── manifest.json
    └── provenance
        └── results.prov.jsonld
```

### Make the Bag

This creates a BDBag archive (bag.tgz) of the data configured in the prior step.

```
smartbag make bag
```

### Generate smartAPI

Next we generate the smartAPI based on the provided metadata.

* Generate code for a smartAPI based on the bag
  * Create a sqlite3 database per tabular file, inserting all rows
  * Generate an OpenAPI interface able to query all rows by each column
  * Add smartAPI specific tags based on accompanying JSON-LD annotations
  
```
smartbag make smartapi --bag bag.tgz --title CTD
```

### Execute the smartAPI

Finally, run the smartAPI. Here's a [link to your server](http://localhost:5000/apidocs/#/) once you've run the command.

```
smartbag run smartapi 
```


## The OpenAPI Interface

The generated user interface looks like this:
![OpenAPI UI](https://github.com/NCATS-Tangerine/smartBag/blob/master/img/image1.png?raw=true)

To query one of the services, use a valid column value like this:
![Query](https://github.com/NCATS-Tangerine/smartBag/blob/master/img/image2.png?raw=true)

It also serves its own self describign JSON-LD metadata:
![OpenAPI UI](https://github.com/NCATS-Tangerine/smartBag/blob/master/img/image3.png?raw=true)

The API makes it easy to introspect example values to help explore the interface.
![OpenAPI UI](https://github.com/NCATS-Tangerine/smartBag/blob/master/img/image4.png?raw=true)

It also serves its own smartAPI schema document.
![OpenAPI UI](https://github.com/NCATS-Tangerine/smartBag/blob/master/img/image5.png?raw=true)

# Applications

This alpha release is applicabile to data stewards or consumers with tabular data.

# Next

Of course, this is preliminary. There is pelenty of room for
* Generating different back ends.
* Generating more of the Research Object metadata infrastructure like the manifest.



  

