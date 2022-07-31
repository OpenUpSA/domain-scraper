# gov.za scraper

Scraper of all government websites. It's starting with the .gov.za top level
domain, but we know that government websites end up on other TLDs too, so we will
have to support those too,

The idea is to scrape and archive everything found on this domain so that it is
readily available for further data extraction and analysis.

The kinds of things this could enable include

- easily finding current tenders across all government websites
- finding public contract data
- finding structured data, e.g. .csv files, shapefiles, etc.
- finding pages or documents matching particular keywords

This tool is focusing on capturing the data in a way that changes are captured
over time to be able to identify changes, but not to provide analytical
functionality. Search/analysis should probably be built on top of this data or
some transformation of this data.


scrape

  - id
  - start timestamp


page

  - observation
  - html
  - sha256
  - etag


file

- observation
  - key
  - sha256
  - etag


canonical_url

  - url


observation

  - scrape
  - url
  - canonical_url
  - referrer

-----

    have a url
    Have we seen it before?
      yes
         do a HEAD request
         does it have an etag?
            yes
              does the previous etag match the current one?
                yes
                  skip this file
                no
            no
      no
    download the file
      capture any content disposition they send
    hash it
    have we seen this hash before?
      yes
        skip this file? (can we log somehow that this hash was observed, perhaps for a different url?)
        maybe store the file row in the db but just don't upload again.
      no
    upload the file to s3 with the hash as its key
    store the file key, etag and hash in db

-----

questions we want to be able to answer using this schema

- when have we seen this file/page?
- what are all the versions of this file/page?
- which pages link to this page/file?
- which files have this extension?
- which urls match this