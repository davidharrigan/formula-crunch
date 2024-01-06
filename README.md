# formula-crunch

`formula-crunch` is an experiment with the [FastF1](https://docs.fastf1.dev/)
Python API to analyze Formula1 driver performance during a race.

The `manage.py` Python script can scrape race data, perform analysis, and store
the result in a SQLite database. Next.js uses the SQLite database to generate
interesting graphics as static pages, so the results can be made available as a
website without any data storage dependency (although the generated graphics are
sized to be suitable for sharing on social media sites).

See an example
[here](https://formula-cunch.vercel.app/races/2022/circuits/spa/drivers/leclerc).

## Scrape data

Scrape driver data

```sh
python manage.py scrape drivers
```

Scrape circuit data

```sh
python manage.py scrape circuites
```

Scrape race data

```sh
python manage.py scrape race --event=<country or circuit name>
```

For more usage info, use the `--help` flag with any sub-command

```sh
python manage.py scrape --help
```

## Database Migration

Generate migration from model changes

```sh
alembic revision --autogenerate -m "added something new"
```

Run migration

```sh
alembic upgrade head
```

Rollback to previous version

```sh
alembic downgrade head-1
```

## Generating UI

Run the UI server

```sh
npm run dev
```
