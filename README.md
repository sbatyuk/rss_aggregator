# RSS Aggregator

An RSS aggregator that ingests feeds at regular intervals and exposes entries via a unified, searchable API.

## Setup

To run the app locally, make sure Docker is installed on your machine. Next you need to initialize the DB:

```shell
cp .env.example .env
docker compose run --rm init-db
```

Now you can run the app with:

```shell
docker compose up
```

Please allow a couple of seconds for the initial feed ingestion to run.

## Features

RSS aggregator `/api/entries` endpoint supports timeline pagination (useful for infinite scrolls), filtering by
hashtags, and semantic search.

### Timeline Pagination

By default, the endpoint returns 30 entries sorted by publication date in descending order:

```shell
curl http://localhost:8000/api/entries/ | jq
```

This can be customized using the following params:

* `before`: returns entries where publication date is strictly before the specified date
* `after`: returns entries where publication date is strictly after the specified date
* `sort` (either `asc` or `desc`): sorts entries by publication date
* `limit`: limits the number of returned entries

To implement infinite scroll, we can simply add a `before` param set to the publication date of the oldest entry from a
previous page:

```shell
curl http://localhost:8000/api/entries/?before=2025-06-29T18:52:21Z | jq
```

### Hashtags

The entries endpoint allows filtering by a list of hashtags. Entries must include all specified hashtags to match:

```shell
curl http://localhost:8000/api/entries/?hashtags=ai&hashtags=openai | jq
```

### Semantic Search

The endpoint supports semantic search using vector similarity over entry titles and summaries:

```shell
curl http://localhost:8000/api/entries/?search=ai+research&limit=5 | jq
```

## Architecture

RSS aggregator app consists of two main components: ingestion pipeline and API.

### Ingestion Pipeline

Ingestion pipeline runs at regular intervals (triggered by [APScheduler](https://github.com/agronholm/apscheduler)) and
consists of the following steps:

1. Asynchronously fetching the feeds using [feedparser](https://github.com/kurtmckee/feedparser). I used an `async`
   implementation primarily as an example, in all other parts of the app I use `sync` approach for simplicity.
2. Transforming raw feed entries into `FeedEntry` model. This also includes:
    * deduplication based on the latest known publication date per feed, under the assumption that older entries are not
      updated
    * hashtag generation (using [KeyBERT](https://github.com/MaartenGr/KeyBERT)) for entries that do not have them
      originally
    * vector embedding generation (using [sentence-transformers](https://github.com/UKPLab/sentence-transformers/))
      based on entry title and summary to support semantic search via Postgresql pgvector extension
3. Loading `FeedEntries` into Postgresql DB. As a final deduplication precaution, `FeedEntry.link` column has a
   unique constraint (the assumption is that every entry has a unique link) and insertion logic leverages Postgresql
   `ON CONFLICT DO NOTHING` feature.

I added extensive exception handling at every stage of the ingestion pipeline where meaningful recovery is possible (
e.g. 5xx HTTP error retries for feed fetching, skipping entries with transformation errors, etc.). At the topmost level
pipeline recovery is guaranteed by `restart: always` in Docker compose service definition.

### API

API is implemented as a simple FastAPI app with a single `/api/entries` endpoint. Query parameters are translated into
SQL queries using SQLModel. Hashtag filtering uses Postgres ARRAY containment, and semantic search leverages pgvector
for vector similarity.

## Technical Considerations

Current implementation of RSS aggregator app serves a proof of concept. For a production ready system we should
reconsider the following choices.

1. Current ingestion scheduling with [APScheduler](https://github.com/agronholm/apscheduler) is very simplistic. For a
   production AWS environment, for example, we may
   consider [scheduled ECS tasks](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/scheduling_tasks.html),
   [Amazon Batch](https://aws.amazon.com/batch/), or similar managed solutions.
2. For more complex ingestion pipelines it may make more sense from a resilience perspective to use workflow
   orchestration platforms like [Temporal](https://temporal.io) or [Amazon SWF](https://aws.amazon.com/swf/).
3. To support user-specific subscriptions, static YAML config should be replaced with a user-managed config. I have
   already added `Feed` model with that in mind.
4. Currently, we ingest feed entries in one big batch. Given a potentially much larger number of feeds in production, we
   would need to split ingestion into parallel tasks each handling a certain number of feeds.
5. For vector embedding generation (current KeyBERT hashtag extraction also leverages embeddings) I used a local
   `all-MiniLM-L6-v2` model which produces good enough results and is faster and cheaper than calling external APIs (
   e.g. OpenAI) at the expense of larger Docker image sizes. We should revisit this decision for production. At some
   point it may be justifiable to extract NLP related code into a separate service or even use external APIs if quality
   becomes a concern.
6. For production, it may be more appropriate to use dedicated vector DBs vs Postgresql pgvector for optimal performance
   under load.
7. While I have added certain DB indexes to optimize query execution, performance must be monitored on an ongoing basis
   in production with necessary indexes/optimizations added based on real usage.
8. I used [SQLModel](https://sqlmodel.tiangolo.com) as an ORM and validation framework for simplicity. But for larger
   projects I would fall back to [SQLAlchemy](https://www.sqlalchemy.org) and [Pydantic](https://pydantic.dev). Using
   SQLModel ties DB and response schemas together, which can reduce flexibility in larger apps.
9. For a production level project, we would also need to add DB migration support
   using [Alembic](https://github.com/sqlalchemy/alembic), for example.
10. Currently, all the feed entry retrieval logic is implemented within the FastAPI router. This is usually problematic
    for larger projects and I would prefer splitting infrastructure and domain logic. This makes the code easier to
    understand, maintain, test, etc.
11. Due to time constraints, I have not covered the code with tests but at least some level of coverage is a must for a
    production level app.
12. Proper logging and metrics instrumentation are also essential for production environments.
13. Docker images may need further improvement over time, e.g. dedicated images per service, multistage builds, etc.
14. To support multi-user functionality, we’d also need authentication, access control, and multi-tenancy-aware data
    modeling.