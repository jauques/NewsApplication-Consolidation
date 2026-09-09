# News Application — Consolidation Capstone

**Author:** Jacques Scheepers  
**Repository:** [NewsApplication-Consolidation](https://github.com/jauques/NewsApplication-Consolidation)

## Overview

This project extends the Django News Application with Git version control, Sphinx documentation, and Docker deployment. Readers browse approved articles, journalists create content, and editors review submissions. The application uses MariaDB and exposes article operations through Django REST Framework.

The Docker image was built and the website manually tested in GitHub Codespaces, demonstrating execution on a computer other than the developer's Windows machine.

This is an educational development deployment. The Dockerfile starts Django's development server; it is not a production hosting configuration. Registration allows role selection for demonstrating the assignment workflows.

## Features and roles

| Role | Website capabilities |
| --- | --- |
| Reader | View approved articles, subscribed articles, and newsletters. |
| Journalist | Create articles for review; manage their own articles and newsletters. |
| Editor | Review, approve, edit, and delete articles; manage publishers and newsletters. |

The project includes token-based API authentication, email uniqueness validation, subscription filtering, and automated API tests. The default email backend prints messages to the console; it does not deliver real emails.

## Project files

| Path | Purpose |
| --- | --- |
| `manage.py` | Django management commands |
| `news/` | Models, forms, views, API serializers, templates, migrations, and tests |
| `news_project/` | Django settings and project URL configuration |
| `docs/source/` | Sphinx configuration and documentation source |
| `docs/build/html/index.html` | Generated documentation homepage |
| `Planning/` | Planning documents and diagrams |
| `Screenshots/` | Application, testing, and deployment evidence |
| `Dockerfile` | Builds the Python application image |
| `compose.yaml` | Runs Django and MariaDB together |
| `.dockerignore` | Excludes private and unnecessary files from the image |
| `.env.example` | Public template for local configuration |
| `.env.docker.example` | Public template for Docker configuration |
| `.gitignore` | Excludes private files, environments, and caches |
| `requirements.txt` | Python dependencies |
| `capstone.txt` | Public repository URL for submission |

## Run locally with a virtual environment

Prerequisites: Python 3.11, Git, and a running MariaDB server. The commands below use Windows PowerShell. Run them from the directory containing `manage.py`.

### 1. Get the project and install dependencies

```powershell
git clone https://github.com/jauques/NewsApplication-Consolidation.git
cd NewsApplication-Consolidation
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 2. Configure MariaDB

For a new installation, open MariaDB as an administrator and run the following SQL, replacing the password placeholder. If you already have `news_db`, keep the existing database and configure Django with an account authorised to use it.

```sql
CREATE DATABASE IF NOT EXISTS news_db CHARACTER SET utf8mb4;
CREATE USER IF NOT EXISTS 'news_user'@'localhost'
    IDENTIFIED BY 'replace-with-your-private-password';
GRANT ALL PRIVILEGES ON news_db.* TO 'news_user'@'localhost';
```

`CREATE USER IF NOT EXISTS` does not change an existing user's password. Use that user's existing credentials or have the database administrator update them.

### 3. Create the private environment file

For a new setup only:

```powershell
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```

Save the generated value privately as `DJANGO_SECRET_KEY` in `.env`. Set the remaining values as follows, replacing the password placeholder:

```env
DJANGO_SECRET_KEY=your-generated-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=
DB_NAME=news_db
DB_USER=news_user
DB_PASSWORD=your-private-database-password
DB_HOST=localhost
DB_PORT=3306
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=news@example.com
```

Settings are loaded through `python-dotenv`. Keep real values out of the example files. Do not overwrite an existing `.env` when updating your checkout.

### 4. Apply migrations and start Django

```powershell
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open [the local website](http://127.0.0.1:8000/) or [Django admin](http://127.0.0.1:8000/admin/). Creating a superuser is optional for the normal registration workflow. Use the registration page to create demonstration accounts with the required roles.

Press `Ctrl+C` to stop the development server. Applying migrations creates or updates tables; it does not copy users or articles from another database.

## Automated tests

With the virtual environment active and MariaDB running:

```powershell
python manage.py test
```

Django creates a separate test database, normally `test_news_db`, and removes it afterwards. The test database account must have permission to create, use, and drop that test database; an account restricted to `news_db` alone cannot run this command. Ask the local database administrator to provide the required test-database permissions if access is denied.

The five existing tests passed locally during consolidation. They cover authenticated article listing, rejection of anonymous article listing, article detail retrieval, journalist creation, and rejection of reader creation. They do not constitute complete coverage of every role, newsletter, or notification workflow. Docker verification additionally included manual website testing in Codespaces; no Docker automated-test pass is claimed here.

## Build and run with Docker

Prerequisites: Docker Engine and Docker Compose, either locally or in GitHub Codespaces. A Python virtual environment is not required to run the containers. Codespaces was used because Docker Desktop was unavailable on the developer's machine.

### 1. Create Docker configuration

From the repository root, on Linux or in Codespaces:

```bash
cp .env.docker.example .env.docker
openssl rand -hex 32
openssl rand -hex 32
openssl rand -hex 32
```

On Windows, the copy command is `Copy-Item .env.docker.example .env.docker`. Only copy the template when creating the private file for the first time.

Open `.env.docker` and put the three generated values into `DJANGO_SECRET_KEY`, `DB_PASSWORD`, and `DB_ROOT_PASSWORD`. Keep them private. Use:

```env
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=
DB_NAME=news_db
DB_USER=news_user
DB_HOST=db
DB_PORT=3306
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=news@example.com
```

Use `news_user`, not `root`, for `DB_USER`: Compose maps it to MariaDB's regular application account. MariaDB configures its root account separately from `DB_ROOT_PASSWORD`. The hostname `db` is the Compose database service name.

Verify that Git ignores the private file:

```bash
git check-ignore -v .env.docker
```

### 2. Start the services

```bash
docker compose --env-file .env.docker config --quiet
docker compose --env-file .env.docker up --build -d
docker compose --env-file .env.docker ps -a
docker compose --env-file .env.docker logs --tail=60 web
```

Compose builds the application image and starts MariaDB 11.4. It waits for the database health check before starting Django. The web container applies migrations and runs on `0.0.0.0:8000`. Confirm the Django startup message in the logs; a container marked “Started” alone does not prove that startup succeeded.

On a local Docker host, open [localhost:8000](http://localhost:8000/). Follow the next section for Codespaces.

### 3. Create demonstration data

The Docker database is separate from the Windows MariaDB database. Existing local users, passwords, and articles are not transferred through GitHub.

Register a Journalist, create an article, register an Editor and approve it, then view it as a Reader. Use distinct email addresses. An optional admin account can be created with:

```bash
docker compose --env-file .env.docker exec web python manage.py createsuperuser
```

The `mariadb_data` named volume preserves data when the containers are stopped or recreated on the same Docker host. It is not a backup and does not move data to another Codespace.

### 4. Stop or restart

```bash
docker compose --env-file .env.docker stop
docker compose --env-file .env.docker start
```

To remove the containers and network while retaining database data:

```bash
docker compose --env-file .env.docker down
```

Do not add `-v` unless intentionally deleting the Docker database volume. Changing MariaDB password variables after the volume is initialised does not automatically change the existing database accounts' passwords.

## GitHub Codespaces

1. Open this repository on GitHub and select `main`, which contains the merged project.
2. Select **Code → Codespaces → Create codespace on main**.
3. In its terminal, check `docker version` and `docker compose version`.
4. Create `.env.docker` as described above.
5. Generate the forwarded website address:

```bash
printf 'https://%s-8000.%s\n' "$CODESPACE_NAME" "$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN"
```

Use the actual hostname in `.env.docker`:

```env
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,YOUR-CODESPACE-HOSTNAME
DJANGO_CSRF_TRUSTED_ORIGINS=https://YOUR-CODESPACE-HOSTNAME
```

Replace `YOUR-CODESPACE-HOSTNAME` with the generated hostname. The allowed-host entry excludes the scheme; the trusted origin includes `https://`. Each new Codespace has its own address.

Build and start Compose as above. Open the **Ports** tab, add port `8000` if necessary, and use **Open in Browser**. Keep port visibility private and sign into GitHub when prompted. The container serves HTTP; the public-facing Codespaces URL uses HTTPS. See [GitHub's port-forwarding guide](https://docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace).

After editing `.env.docker`, load its new values by recreating the web container:

```bash
docker compose --env-file .env.docker up -d --no-deps --force-recreate web
```

The Codespaces website is temporary and depends on the Codespace being active. The repository URL in `capstone.txt` is the submission link, not the temporary website address.

## Troubleshooting from this deployment

### CSRF errors

For “Origin checking failed,” verify the exact reported origin against `DJANGO_CSRF_TRUSTED_ORIGINS`. During this deployment, requests were reported with `https://localhost:8000`, so that exact origin was added alongside the Codespaces origin for this development environment. Add it only if your request actually uses it.

For “CSRF token from POST incorrect,” reopen the form in a fresh browser session, sign into GitHub if required, and avoid submitting a stale form after logging in elsewhere. This resolved the token issue during manual testing. Do not disable CSRF middleware.

### Database connection timeout in Codespaces

The database was healthy and `db` resolved correctly, but TCP connections to port 3306 timed out. Inspection showed both newer and legacy firewall tables. The legacy forwarding policy dropped traffic on the project's bridge, while its rules only covered `docker0`.

In the personal Codespace used for testing, a narrow legacy `DOCKER-USER` rule allowing traffic within that specific project bridge resolved the timeout. This was an environment-specific workaround, not a normal installation step or a change to the application.

Diagnostic commands used:

```bash
docker compose --env-file .env.docker ps -a
docker compose --env-file .env.docker logs --tail=60 db
docker compose --env-file .env.docker run --rm --no-deps web python -c "import socket; print(socket.gethostbyname('db'), flush=True); connection = socket.create_connection(('db', 3306), timeout=5); print('Database TCP connection successful'); connection.close()"
ip -4 route
sudo iptables -L FORWARD -n -v
sudo iptables-legacy -L FORWARD -n -v
```

Only after confirming this same cause, and with authority to administer the environment, the workaround has this form. Replace `PROJECT_BRIDGE` with the verified bridge interface for this Compose network; do not run the placeholder literally:

```bash
sudo iptables-legacy -I DOCKER-USER 1 -i PROJECT_BRIDGE -o PROJECT_BRIDGE -j ACCEPT
```

Undo it with:

```bash
sudo iptables-legacy -D DOCKER-USER -i PROJECT_BRIDGE -o PROJECT_BRIDGE -j ACCEPT
```

The bridge name can change when the network is recreated, and firewall changes may not persist after environment restarts. Do not globally disable the firewall or change its default policy. Managed environments should have their administrator resolve the conflict. See [Docker's firewall documentation](https://docs.docker.com/engine/network/packet-filtering-firewalls/).

## API reference

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/api-token-auth/` | Obtain a DRF token with a username and password |
| GET | `/api/articles/` | List approved articles for an authenticated user |
| POST | `/api/articles/` | Create an article as a Journalist |
| GET | `/api/articles/subscribed/` | Retrieve approved articles matching the user's subscriptions |
| GET | `/api/articles/<id>/` | Retrieve an article subject to approval and role rules |
| PUT / PATCH | `/api/articles/<id>/` | Update as an Editor or the owning Journalist |
| DELETE | `/api/articles/<id>/` | Delete as an Editor or the owning Journalist |

Send token credentials to `/api-token-auth/` as `username` and `password` fields. Use the returned token on subsequent API requests:

```text
Authorization: Token YOUR_PRIVATE_TOKEN
```

Website login uses sessions; the API uses DRF token authentication. Editors approve articles through the website's editor dashboard. Do not publish API tokens in screenshots or repository files.

## Sphinx documentation

The documentation source and generated HTML are included in Git. Open `docs/build/html/index.html` locally to browse the documentation. GitHub's file view does not itself host the HTML as a website; GitHub Pages is not configured by these instructions.

To rebuild from the repository root with the virtual environment active, dependencies installed, and `.env` configured:

```powershell
python -m sphinx -b html docs/source docs/build/html
```

Sphinx loads `news_project.settings` and calls `django.setup()` to import Django models and views. Autodoc extracts docstrings, Napoleon formats their Returns/Raises sections, and Viewcode provides source links. Temporary `.doctrees` caches are ignored; generated HTML remains committed.

If adding new Python modules, regenerate the reference pages before building:

```powershell
python -m sphinx.ext.apidoc -o docs/source news news/migrations
```

## Version control and submission

- `main`: merged application, documentation, and Docker configuration.
- `docs`: docstring improvements committed per script and Sphinx documentation.
- `container`: Docker configuration and deployment work.

The documentation and container branches were created from `main` and merged back. A `.gitignore` conflict was resolved while retaining both Sphinx-cache exclusions and private Docker-environment exclusions.

To inspect the history:

```bash
git --no-pager log --oneline --graph --all
```

`capstone.txt` contains the public repository link. Planning documents and screenshots accompany the source. Private `.env` and `.env.docker` files, virtual environments, and Python caches are excluded from submission and Git. Review screenshots for secrets before publishing them.
