# smartBag

## Bagit Conetxt

The emerging ecosystem of complementary conventions for archiving data sets suggests a big opportunity for making data machine readable on a large scale.

* [Bagit](https://en.wikipedia.org/wiki/BagIt) is a file packaging protocol.
* [Bagit-RO](https://github.com/ResearchObject/bagit-ro) integrates the Bagit and Research Object frameworks.
* [BDBags](http://bd2k.ini.usc.edu/tools/bdbag/) extends Bagit-RO so that referenced data files may be remote, referenced via ids with checksums.

## Challenge

The NCATS Data Translator is annotating federated web APIs with semantic information. This makes biomedical data amenable to automated discovery, access, and reasoning. But

* **Development**: IT projects to expose data as web APIs are tedious and expensive.
* **Technology**: The underlying technologies to do this are in perpetual flux.

## Make it Go

It would be better to

  * **Annotate**: Annotate data archives with appropriate semantica and ontological metadata.
  * **Generate**: Compile the data and semantics to publish them into various evolving tech pipelines.

### Annotation

So we're developing a tool chain to let (optimally) data stewards or (pragmatically) data consumers semantically annotate their data sources. The Data Translator uses JSON-LD and globally unique identifiers to build robust metadata about web APIs. This is all done according to the [smartAPI](http://smart-api.info/) approach.

The smartBag tool chain adopts both components, providing a mechanism to annotate tabular data with JSON-LD.

### Generation

The seconds step is to illustrate the utility of the metadata by generation a smartAPI from a properly annotated bag. This technique will allow data stewards to focus on meta data and give software developers the openness they need to target arbitrary data delivery and execution platforms.

## Getting Started

Try these steps to get started
```
git clone <repo> 
cd <repo>/ctd
./all
```

This script will do a number of things:

* Create a data directory above the repo
* Download all CTD files
* Build a BDBag with semanti annotations for a couple of files by way of example.
* Generate code for a smartAPI based on the bag
  * Create a sqlite3 database per tabular file, inserting all rows
  * Generate an OpenAPI interface able to query all rows by each column
  * Add smartAPI specific tags based on accompanying JSON-LD annotations
* Start the API on port 5000

## The OpenAPI Interface

The generated user interface looks like this:
![OpenAPI UI](https://github.com/NCATS-Tangerine/smartBag/blob/master/img/smart-api-1.png?raw=true)
