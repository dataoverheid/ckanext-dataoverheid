# ckanext-dataoverheid

CKAN extension used by [Data.Overheid.nl](https://data.overheid.nl) to implement the [DCAT-AP-DONL 1.1](https://dcat-ap-donl.readthedocs.io) metadata standard into CKAN.

This extension is meant to be used for CKAN installations *not* running as a front-end system, but rather as a back-end system only accessed through the CKAN API. As such it does not modify any of the CKAN front-end features. When this extension is running it will no longer be possible to perform dataset mutations (with the exception of deletions) via the CKAN web interface. User, Group and Organization mutations will continue to function as expected via the web interface.

## Contact

- Web: [data.overheid.nl/contact](https://data.overheid.nl/contact)
- Email: [opendata@overheid.nl](mailto:opendata@overheid.nl)

## License

Licensed under the [CC0](https://creativecommons.org/publicdomain/zero/1.0/) license. [Full license text](https://creativecommons.org/publicdomain/zero/1.0/legalcode)

## Requirements

Minimum version requirements:

| Software | Version  |
|----------|----------|
| Python   | \>=2.7   |
| CKAN     | \>=2.8   |
| Solr     | \>=8.0   |

The CKAN extension occasionally makes HTTP(S) requests to [waardelijsten.dcat-ap-donl.nl](https://waardelijsten.dcat-ap-donl.nl) and [data.overheid.nl](https://data.overheid.nl), ensure that your firewall allows these requests.

## Installation

Assuming a standard (empty) CKAN installation on a Ubuntu server; follow these steps to install and configure this extension.

### CKAN
From your terminal of choice:
```bash
. /usr/lib/ckan/default/bin/activate
cd /usr/lib/ckan/default/src/
python -m pip install -e git+https://github.com/dataoverheid/ckanext-dataoverheid.git#egg=ckanext-dataoverheid --no-cache-dir
python -m pip install -r /usr/lib/ckan/default/src/ckanext-dataoverheid/requirements.txt --no-cache-dir
```

Edit your `production.ini` (or `development.ini`) and ensure the following key/value pairs are present (both files should be located in `/etc/ckan/default/`:

```ini
solr_url = http://127.0.0.1:8983/solr/donl_dataset
licenses_group_url = file:///usr/lib/ckan/default/src/ckanext-dataoverheid/ckanext/dataoverheid/resources/vocabularies/ckan_license.json
ckan.mimetype_guess = None
ckan.plugins = donl-authorization donl-scheme donl-rdf donl-interface
```

*Do note that the `donl-authorization` plug-in is optional, it allows individual users to perform dataset_purge actions via the CKAN API when they are registered as the `creator_user_id` of said dataset.*

### CRON

Add the following two entries to the crontab of the Linux user running CKAN (probably `www-data`):

```bash
30 23 * * * (cd /usr/lib/ckan/default/src/ckanext-dataoverheid && /usr/lib/ckan/default/bin/python2.7 ckanext/dataoverheid/task/ckan_updater.py --list=vocabulary)
35 23 * * * (cd /usr/lib/ckan/default/src/ckanext-dataoverheid && /usr/lib/ckan/default/bin/python2.7 ckanext/dataoverheid/task/ckan_updater.py --list=taxonomy)
```

Afterwards, execute these commands:

```bash
sudo su {CKAN_USER}
. /usr/lib/ckan/default/bin/activate
cd /usr/lib/ckan/default/src/ckanext-dataoverheid
python ckanext/dataoverheid/task/ckan_updater.py --list=vocabulary
python ckanext/dataoverheid/task/ckan_updater.py --list=taxonomy
```

### Solr

To create and configure your Solr core for CKAN:

```bash
sudo -u solr /opt/solr/bin/solr create -c donl_dataset
sudo rm -rf /var/solr/data/donl_dataset/conf
sudo ln -sf /usr/lib/ckan/default/src/ckanext-dataoverheid/ckanext/dataoverheid/resources/solr/donl_dataset /var/solr/data/donl_dataset/conf
sudo service solr restart
```

Now, as the {CKAN_USER}:

```bash
sudo su {CKAN_USER}
. /usr/lib/ckan/default/bin/activate
cd /usr/lib/ckan/default/src/ckanext-dataoverheid
python ckanext/dataoverheid/task/solr_updater.py
```

### Finishing up

Flush the Redis cache and restart CKAN:

```bash
redis-cli FLUSHALL
sudo service apache2 restart
```

Your CKAN installation is now operational and running with the `ckanext-dataoverheid` extension.
