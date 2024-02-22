# Changelog


## 2.2.3 (2024/02)

- Futurize Extension
- Remove IDatasetForm and IPackageController Interfaces from SchemaPlugin

## 2.2.2 (2020/09)

- Bugfix for RDF export of dataset metadata.
- Added support for the "Ministerie van Sociale Zaken en Werkgelegenheid" community.

## 2.2.1 (2020/08)

- Bugfix to properly cache the `transformations` key of `config.json` in Redis.
- Updated `donl_search` Solr schema to properly mark the `language` field als multivalued.

## 2.2.0 (2020/07)

- Started maintaining the `CHANGELOG.md` to track changes between versions.
- Introduced `CONTRIBUTING.md` detailing how contributions to this project can be made.
- Max line length of 80 characters is now enforced throughout the codebase in accordance with PEP8.
- Refactored Spatial validation. The validation rules are now set in the `config.json` file greatly reducing the code complexity of validation a Spatial property.
- Moved several hardcoded strings to `config.json`.
- The transformation mapping used to transform packages before they are sent to Apache Solr has been moved to the `config.json` file.
- The "Latest mutations" block on the CKAN homepage now explicitly sorts the packages by `metadata_modified desc`.
- Slight refactor work was done to how config data is retrieved from Redis.

## 2.1.5 (2020/06)

- Removed unused Solr clustering component.
- Expanded theme hierarchy logic during query time.
- New requestHandler for searching through catalogs.
- Changed autocomplete_identifier requestHandler to a search component rather than a suggest component.
- Changed dataset logic for migratie community.
- Updated scheduled tasks to include new managed resource for query time searching through the hierarchical themes.

## 2.1.4 (2020/05)

- Introduced Solr requestHandler for searching through communities 'select_community'.
- Expanded ruleset for 'onderwijs' community by accepting additional themes.
- Updated README.md installation instructions.
- Optimized Solr indexaction scripts by reducing the amount of Solr commits per execution.
- Some small corrections in Solr requestHandlers select_news and select_support.
- Increased default autocomplete result count for back-end forms.

## 2.1.3 (2020/04)

- Updated solr url in config.json for dockerized deployments.

## 2.1.2 (2020/03)

- Bugfix for `epsg28992` validator.
- Bugfix for handler `related_content` for non dataset.
- Support for additional communities during community extraction.
- Two new Solr requesthandlers for Drupal contentpages (`select_news`, `select_support`).

## 2.1.1 (2020/03)

No data available.

## 2.1.0 (2020/02)

No data available.

## 2.0.0 (2019/10)

No data available.

## 1.0.0 (2019/10)

No data available.
