# Docker + PostgreSQL Setup (Optional)

CoCo works out of the box with SQLite -- no Docker required. This guide covers the optional PostgreSQL backend for production-grade episodic memory.

## When to Use PostgreSQL

**Stick with SQLite (default) if you:**
- Run CoCo on a single machine
- Want zero-configuration setup
- Are just getting started

**Consider PostgreSQL if you:**
- Need multi-session concurrent access
- Want production-grade persistence and backups
- Plan to run CoCo as a long-running service

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed and running
- [Docker Compose](https://docs.docker.com/compose/install/) (included with Docker Desktop)

Verify Docker is available:

```bash
docker --version
docker compose version
```

## Quick Start

### 1. Start the Database

A `docker-compose.yml` is included in the project root:

```bash
docker compose up -d
```

This starts a PostgreSQL 16 (Alpine) container named `coco-postgres` on port 5432.

### 2. Configure CoCo

Add these to your `.env` file:

```bash
# Database backend (default: sqlite)
COCO_DB_BACKEND=postgresql

# Connection settings (these are the defaults)
DB_HOST=localhost
DB_PORT=5432
DB_USER=cocoa
DB_PASSWORD=change_me_in_production
DB_NAME=cocoa_db
```

Change `DB_PASSWORD` to a secure value for any non-local deployment.

### 3. Launch CoCo

```bash
./launch.sh
```

The launch script automatically detects Docker and waits for the database to be ready (up to 30 seconds).

## Verify Connection

Check that the PostgreSQL container is running and healthy:

```bash
docker compose ps
```

Expected output:

```
NAME            STATUS          PORTS
coco-postgres   Up (healthy)    0.0.0.0:5432->5432/tcp
```

Test database connectivity directly:

```bash
docker compose exec coco-db pg_isready -U cocoa -d cocoa_db
```

Should print: `cocoa_db - accepting connections`

## Database Management

### Stop the database

```bash
docker compose down
```

Data is preserved in a Docker volume (`coco_pgdata`).

### Stop and delete all data

```bash
docker compose down -v
```

This removes the volume. All episodic memory data will be lost.

### View logs

```bash
docker compose logs -f coco-db
```

## What Each Database Stores

CoCo uses three databases regardless of backend choice:

| Database | Backend | Purpose |
|----------|---------|---------|
| Episodic memory | PostgreSQL **or** SQLite | Conversation history, context |
| Facts memory | SQLite (`coco_memory.db`) | 18 fact types for perfect recall |
| Semantic memory | SQLite (`simple_rag.db`) | Embeddings and document search |

Only episodic memory is affected by the PostgreSQL option. Facts and semantic memory always use SQLite.

## Troubleshooting

### "connection refused" on port 5432

Ensure the container is running: `docker compose ps`. If not, start it with `docker compose up -d` and wait a few seconds for the health check to pass.

### Port 5432 already in use

Another PostgreSQL instance or service is using the port. Change the port in `.env`:

```bash
DB_PORT=5433
```

Then restart: `docker compose down && docker compose up -d`

### Docker not installed

CoCo falls back to SQLite automatically. No action needed unless you specifically want PostgreSQL.
