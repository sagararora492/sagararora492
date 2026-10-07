# Toolkit icons

`scripts/build_assets.py` inlines these icons into the Toolkit card and recolours
them to the theme's accent colour.

| Icons | Source | Licence |
| --- | --- | --- |
| snowflake, bigquery, spark, python, prefect, kafka, gcp, terraform, docker, githubactions, anthropic, gemini | [Simple Icons](https://simpleicons.org/) | CC0 1.0 |
| dbt, openai | [gilbarbara/logos](https://github.com/gilbarbara/logos) | CC0 1.0 |
| aws, azure, airflow | [Devicon](https://devicon.dev/) (plain variants) | MIT |
| sql, fivetran, structured, agents, citations | Drawn for this repo (generic symbols; no Fivetran logo is published in an open icon set) | — |

Brand logos are trademarks of their owners and are used here only to name the tools.

To add a tool, drop a single-colour SVG here (fetching from
`https://api.iconify.design/<set>/<name>.svg` works well), reference it in `TOOLKIT`,
and run `python3 scripts/build_assets.py`.
