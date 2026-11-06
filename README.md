# Simple catalog frontend list of items + tg bot + backend

Create item with title + image for catalog using bot as admin. User see such items in plain card list on index page by direct access or through TMA

> **Stack**: Next.js for frontend, aiogram for bot, fastapi + sqlalchemy + alembic for backend
>
> **Infra**: DB: Postgres, redis for bot, nginx for fast and convient deploy

## How to use

Fill [env](.env) by [env example](.env.example)

#### Init database by run alembic

##### If there no versions, create one by running:

```
docker-compose exec backend alembic revision --autogenerate -m "<message>"
```

After that apply versions

```sh
docker-compose exec backend alembic upgrade head
```

#### Start compose

> By default development build are running (see [compose override](compose.override.yaml))

```sh
docker-compose up
```

### Production

```sh
docker-compose -f compose.yaml -f compose.prod.yaml up -d
```

### Unused features

Bot `/validate` currently exists and used in backend (proxied) and could be used futher on frontend when need acquire user, for now it "just exists"
