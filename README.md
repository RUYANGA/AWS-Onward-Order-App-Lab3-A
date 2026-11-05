# AWS-Onward-Order-App-Lab3-A

The Onward Logistics order application: one Django app that serves both the web page (merchants book deliveries and see recent orders) and the order logic (pricing, delivery estimates, validation), packaged as **one container image**. Infrastructure lives in [`AWS-Onward-Order-Infra-Lab3-A`](https://github.com/RUYANGA/AWS-Onward-Order-Infra-Lab3-A).

## Project structure

```
.
├── src/                          # All application source code
│   ├── apps/
│   │   ├── core/                 # Cross-cutting: health check, runtime info, page context
│   │   │   ├── health.py         # /health payload (status, release, task, AZ)
│   │   │   ├── middleware.py     # answers ALB/ECS health checks before host checks
│   │   │   ├── runtime.py        # reads the ECS task id and AZ shown on the page
│   │   │   ├── context_processors.py  # name, lab, release, env on every page
│   │   │   ├── views.py, urls.py
│   │   │   └── tests/
│   │   └── orders/               # Booking deliveries
│   │       ├── constants.py      # zones, services, pricing rules
│   │       ├── exceptions.py     # OrderError (message shown to the user)
│   │       ├── services/
│   │       │   ├── pricing.py    # quote(): price + delivery days
│   │       │   └── order_book.py # in-memory, thread-safe order store
│   │       ├── api/
│   │       │   ├── views.py      # /api/quote, /api/orders (JSON)
│   │       │   └── urls.py
│   │       ├── views.py, urls.py # the booking page: / and the form post /orders
│   │       ├── templates/orders/index.html
│   │       ├── static/orders/style.css
│   │       └── tests/            # pricing, order book, page, api/
│   └── config/
│       ├── settings/
│       │   ├── base.py           # shared settings + lab values (STUDENT_NAME)
│       │   ├── dev.py            # local development
│       │   ├── prod.py           # ECS (default in the image)
│       │   └── test.py           # test runner
│       ├── urls.py, wsgi.py, asgi.py
├── manage.py
├── requirements/                 # base / dev / prod  (requirements.txt -> prod)
├── deploy/appspec.yaml           # tells CodeDeploy which container to swap
├── scripts/
│   ├── build-deploy-bundle.sh    # builds the release hand-off (taskdef.json + appspec.yaml)
│   ├── load-test.sh              # drives load to demonstrate auto scaling
│   └── django-manage.sh          # manage.py wrapper used by pre-commit
├── .github/workflows/
│   ├── ci.yml                    # pull request -> lint + tests
│   ├── release.yml               # merge to main -> test -> build -> push -> release
│   └── rollback.yml              # re-release a previous image by git SHA
├── Dockerfile                    # multi-stage (uv), non-root, read-only friendly
├── docker-compose.yml            # runs the production image locally like ECS
├── pyproject.toml, .flake8, .pre-commit-config.yaml, pyrightconfig.json
└── .env.example
```

## Before your first push

Set your name, which is shown on every page: change the `STUDENT_NAME` default in [`src/config/settings/base.py`](src/config/settings/base.py) (or set the `STUDENT_NAME` environment variable).

## Routes

| Path | What it does |
|---|---|
| `GET /` | Booking form and the recent orders on the task that answered |
| `POST /orders` | Form post (CSRF protected), redirects to `/?placed=ONW-…` |
| `GET /api/quote?zone=&service=&weight_kg=` | Price and delivery days |
| `GET /api/orders`, `POST /api/orders` | List or book orders as JSON (used by `scripts/load-test.sh`) |
| `GET /health` | ALB target group and ECS container health check |

These paths, port 8000 and the read-only root filesystem are the contract with the infrastructure repository; keep them stable.

## How a change reaches customers

1. Open a pull request. *CI* runs pre-commit (ruff, flake8, bandit, shellcheck, hadolint, Django checks) and the tests.
2. Merge to `main`. This is the only manual step.
3. *Build and release* runs the tests, builds the image and smoke-tests it with a read-only filesystem as a non-root user.
4. It assumes `onward-prod-github-actions` through **GitHub OIDC**. No AWS keys are stored in this repository or in GitHub secrets; the role only trusts this repository's `main` branch.
5. It pushes the image tagged with the full git SHA, uploads `deploy-bundle.zip` to S3, then moves the `latest` tag.
6. The `latest` push fires an EventBridge rule, CodePipeline starts, and CodeDeploy performs a blue/green release (10% canary for 5 minutes, automatic rollback on alarm).

The page shows the release (short git SHA) and which task and AZ answered, so you can watch it change.

## Repository variables

Set in *Settings > Secrets and variables > Actions > Variables*. None are secrets.

| Variable | Example |
|---|---|
| `AWS_REGION` | `eu-west-1` |
| `AWS_ROLE_ARN` | output `GitHubActionsRoleArn` of `onward-prod-delivery-foundation` |
| `ECR_REPOSITORY` | `onward-prod-order-app` |
| `TASK_FAMILY` | `onward-prod-order-app` |
| `DEPLOY_BUCKET` | output `DeployBundleBucketName` |

## Run locally

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements/dev.txt
cp .env.example .env                      # optional: set STUDENT_NAME there
pre-commit install                        # run the checks on every commit

python manage.py test apps --settings=config.settings.test
python manage.py runserver 8000           # dev settings, http://localhost:8000

# The production image, run the way ECS runs it (read-only, /tmp only):
docker compose up --build
```

## Settings

`DJANGO_SETTINGS_MODULE` is `config.settings.dev` for `manage.py`, `config.settings.test` for tests and `config.settings.prod` in the image. Values come from environment variables or a local `.env` file; none are required on ECS, where the task definition sets `APP_ENV` and `PORT` and the image sets `APP_VERSION`.

| Env var | Default | Purpose |
|---|---|---|
| `STUDENT_NAME` | see `base.py` | Shown on every page |
| `APP_VERSION` | `local` | Release shown on the page and in `/health` (build arg) |
| `APP_ENV` | `local` | Environment stamp on the page (`prod` on ECS) |
| `ALLOWED_HOSTS` | `*` | Set to the ALB DNS name to restrict; `/health` works with any host |
| `CSRF_TRUSTED_ORIGINS` | empty | Add `https://your-domain` when HTTPS is in front of the ALB |
| `USE_HTTPS` | `false` | Production only: HTTPS redirect, secure CSRF cookie and HSTS. The lab ALB is HTTP only, so leave it off until an HTTPS listener exists |
| `SECRET_KEY` | random per process | Nothing is signed today (no sessions or login); set it if that changes |
| `LOG_LEVEL` | `INFO` | Root log level |

There is no database (orders are in memory) and so no migrations. Static files are collected into the image at build time and served by WhiteNoise, so nothing is written outside `/tmp` at runtime.

## Rolling back

During a release the alarms roll back automatically, or use *Stop and roll back* in CodeDeploy. For up to 15 minutes after a release the previous version is still running and the same button switches traffic back instantly. After that, run *Roll back to a previous release* with the git SHA of a good build; it re-releases that exact image without rebuilding. Then fix forward with a `git revert`.

## Note on data

Orders are kept in memory per container (per gunicorn worker), enough to demonstrate the application. A production version would store them in a database such as DynamoDB, reached through a gateway VPC endpoint so the no-internet rule still holds.
