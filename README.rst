Stanford Litigation DB Scraper
===================================

`Scrapy <http://scrapy.org/>`__ project for scraping the Stanford 
`Securities Class Action Clearinghouse <http://securities.stanford.edu/filings.html>`__.


Use
------------

.. code-block:: bash

    git clone https://github.com/gaulinmp/lit_scrape.git
    cd lit_scrape
    scrapy crawl -o lit_data.json -t json --logfile lit_log.log seclit

This will make two files, `lit_data.json` and a log file you can ignore.
The former will be a json dump of the litigation database.
Turn it into a pandas dataframe like so:

.. code-block:: python

    import re, json
    import pandas as pd
    re_date = re.compile('[01]\d/[0123]\d/[12]\d\d\d')
    clean_dat = []
    with open('lit_data.json') as fh:
        for row in json.load(fh):
            tmp = {}
            for k,v in row.items():
                if k == 'description': 
                    continue
                if k == 'url':
                    tmp[k] = v
                    continue
                if k == 'status':
                    _ = [_v.strip() for _v in v if _v.strip()]
                    tmp[k] = _[0]
                    tmp[k+'_long'] = '|'.join(_)
                    _ = re_date.search(tmp[k+'_long'])
                    tmp[k+'_date'] = _.group(0) if _ else None
                    continue
                tmp[k] = v[0].strip() if v[0].strip() else None
                if k == 'company' and 'Defendant: ' in v[0]:
                    tmp[k] = tmp[k].replace('Defendant: ', '')
            clean_dat.append(tmp)
    df_lit = pd.DataFrame(clean_dat)
    for c in 'class_start class_end date_filed status_date'.split():
        df_lit[c] = pd.to_datetime(df_lit[c])
