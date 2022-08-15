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


questions we want to be able to answer using this data

- when have we seen this file/page?
- what are all the versions of this file/page?
- which pages link to this page/file?
- which files have this extension?
- which urls match this text?
- which pages match this text?
- which file names match this text?
- which files match this text?

And eventually extract structured data regularly, like keeping a list of open
tenders up to date.

## Running the scraper

### Using docker-compose (e.g. in development)

    docker-compose run --rm scraper poetry run scrapy crawl govza


### Using docker directly (e.g. in production)

Set the following environment variables:

- AWS_S3_BUCKET_NAME
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_S3_ENDPOINT_URL or leave it unset to use the default
- DATABASE_URL (postgresql://... for postgres)

Run the following command in the container:

    poetry run scrapy crawl govza