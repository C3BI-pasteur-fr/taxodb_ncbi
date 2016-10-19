`taxodb_ncbi.py` is a simple *python* script used to format the *[NCBI taxonomy Database](http://www.ncbi.nlm.nih.gov/taxonomy)*.
It requires *[bsddb3](https://pypi.python.org/pypi/bsddb3)* python library and *[Berkeley DB library](http://www.oracle.com)* to work.

## INSTALL
1. Install *Berkeley DB*

* *Mac OSX*
```
brew install berkeley-db4
```
* *Ubuntu/Debian*
```
sudo apt-get install libdb-dev
```
* *CentOS*
```
sudo yum install libdb-devel
```
2. Install `bsddb3`

```
$ pip install bsddb3
```
3. Install *python* script

```
$ python setup.py install
```

## GETTING DATA

`taxodb_ncbi.py` only requires 'Taxonomy nodes' (`nodes.dmp`) and 'Taxonomy names' (`names.dmp`) files to work.
These files are provided within *[NCBI Taxonomy database](http://www.ncbi.nlm.nih.gov/taxonomy)*.

Download required files from NCBI taxonomy database:
```
  $ wget ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz
  $ tar zxf taxdump.tar.gz
```

## USAGE
```
$ python taxodb_ncbi.py -h
usage: taxodb_ncbi.py [-h] -n file -d file [-k File] [-t File] [-b File]
                      [-f string]

program uses to format the NCBI Taxonomy Database

optional arguments:
  -h, --help            show this help message and exit

Options:
  -n file, --names file
                        names.dmp from NCBI taxonomy databank (default: None)
  -d file, --nodes file
                        nodes.dmp from NCBI taxonomy databank (default: None)
  -k File, --flatdb File
                        Output file: flat databank format. (default: None)
  -t File, --tab File   Output file: tabulated format. Organism with
                        classification. (default: None)
  -b File, --bdb File   Output file: Berleley db format (default: None)
  -f string, --format string
                        By default, reports only full taxonomy ie taxonomies
                        that have 'species', 'subspecies' or 'no rank' at the
                        final position. Otherwise, reports all taxonomies even
                        if they are partial (default: full)
```

## RUNNING

Create Berkeley DB database and associated databank and tabulates files:
```
python taxodb_ncbi.py -n names.dmp -d nodes.dmp -k taxodb_ncbi.out -t taxodb_ncbi.out -b taxodb_ncbi.bdb
```


