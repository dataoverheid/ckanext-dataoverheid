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
| Python   | \>=2.6   |
| CKAN     | \>=2.5   |
| Solr     | \>=5.3   |

The CKAN extension occasionally makes HTTP(S) requests to [waardelijsten.dcat-ap-donl.nl](https://waardelijsten.dcat-ap-donl.nl) and [data.overheid.nl](https://data.overheid.nl), ensure that your firewall allows these requests.

## Installation

Assuming a standard (empty) CKAN installation on a Ubuntu server; follow these steps to install and configure this extension.

### CKAN
From your terminal of choice:
```bash
/usr/lib/ckan/default/bin/activate
cd /usr/lib/ckan/default/src/
pip install -e git+https://github.com/dataoverheid/ckanext-dataoverheid.git#egg=ckanext-dataoverheid
pip install -r /usr/lib/ckan/default/src/ckanext-dataoverheid/requirements.txt

```

Edit your `production.ini` (or `development.ini`) and ensure the following key/value pairs are present (both files should be located in `/etc/ckan/default/`:

```ini
solr_url = http://127.0.0.1:8983/solr/ckan
licenses_group_url = https://waardelijsten.dcat-ap-donl.nl/overheid_license.json
ckan.mimetype_guess = None
ckan.plugins = donl-authorization donl-scheme

```

*Do note that the `donl-authorization` plug-in is optional, it allows individual users to perform dataset_purge actions via the CKAN API when they are registered as the `creator_user_id` of said dataset.*

### CRON

Add the following two entries to the crontab of the Linux user running CKAN (probably `www-data`):

```bash
30 23 * * * (cd /usr/lib/ckan/default/src/ckanext-dataoverheid && python ckanext/dataoverheid/task/controlled_vocabulary_updater.py)
45 23 * * * (cd /usr/lib/ckan/default/src/ckanext-dataoverheid && python ckanext/dataoverheid/task/solr_dynamic_files_updater.py)
```

Afterwards, execute these two entries manually:

```bash
(sudo -u {CKAN_USER} && cd /usr/lib/ckan/default/src/ckanext-dataoverheid && python ckanext/dataoverheid/task/controlled_vocabulary_updater.py)
(sudo -u {CKAN_USER} && cd /usr/lib/ckan/default/src/ckanext-dataoverheid && python ckanext/dataoverheid/task/solr_dynamic_files_updater.py)

```

### Solr

To create and configure your Solr core for CKAN:

```bash
sudo -u solr /opt/solr/bin/solr create -c ckan
sudo rm /var/solr/data/ckan/conf/protwords.txt
sudo rm /var/solr/data/ckan/conf/solrconfig.xml
sudo rm /var/solr/data/ckan/conf/managed-schema
sudo rm /var/solr/data/ckan/conf/stopwords.txt
sudo rm /var/solr/data/ckan/conf/synonyms.txt
sudo mkdir /var/lib/solr
sudo chown solr /var/lib/solr -R
sudo ln -sf /usr/lib/ckan/default/src/ckanext-dataoverheid/ckanext/dataoverheid/resources/solr/5.3/ /var/solr/data/ckan/conf/

```

### Finishing up

Restart both CKAN and Solr:

```bash
sudo service solr restart
sudo service apache2 restart

```

Your CKAN installation is now operational and running with the `ckanext-dataoverheid` extension.
