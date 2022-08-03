# formula-crunch

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
