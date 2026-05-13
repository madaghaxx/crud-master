# CRUD-MASTER

A microservices movie streaming platform using an **API Gateway**, **Inventory API**, and **Billing API** — each running in its own Vagrant virtual machine.

## Architecture

```
Host (localhost:8080)
        │
        ▼
┌──────────────────┐        HTTP         ┌──────────────────────┐
│   gateway-vm     │ ─────────────────▶  │    inventory-vm      │
│ 192.168.56.12    │                     │  192.168.56.11:8080  │
│ Flask Gateway    │                     │  Flask + PostgreSQL   │
│ Port 8080        │                     │  (movies_db)         │
└──────────────────┘                     └──────────────────────┘
        │
        │  RabbitMQ (disabled — billing-vm not active)
        ▼
┌──────────────────┐
│   billing-vm     │  ← currently commented out
│ 192.168.56.13    │
└──────────────────┘
```

## Stack

| Component       | Technology                              |
|-----------------|-----------------------------------------|
| API Gateway     | Python 3, Flask, PM2                    |
| Inventory API   | Python 3, Flask, SQLAlchemy, PostgreSQL |
| Billing API     | Python 3, pika (RabbitMQ) — disabled    |
| VM management   | Vagrant + VirtualBox                    |
| Process manager | PM2                                     |

## Prerequisites

- [VirtualBox](https://www.virtualbox.org/)
- [Vagrant](https://www.vagrantup.com/)
- Postman (for testing)

## Environment Variables

All variables are defined in `.env` at the project root. This file is committed intentionally for this exercise.

| Variable               | Description                              | Default            |
|------------------------|------------------------------------------|--------------------|
| `INVENTORY_VM_IP`      | IP of inventory-vm                       | `192.168.56.11`    |
| `GATEWAY_VM_IP`        | IP of gateway-vm                         | `192.168.56.12`    |
| `INVENTORY_API_URL`    | URL gateway uses to reach inventory      | `http://192.168.56.11:8080` |
| `INVENTORY_DB_NAME`    | PostgreSQL database name                 | `movies_db`        |
| `INVENTORY_DB_USER`    | PostgreSQL user                          | `inventory_user`   |
| `INVENTORY_DB_PASSWORD`| PostgreSQL password                      | `inventory_password` |
| `INVENTORY_DB_HOST`    | DB host (inside inventory-vm)            | `127.0.0.1`        |
| `INVENTORY_DB_PORT`    | DB port                                  | `5432`             |
| `RABBITMQ_HOST`        | RabbitMQ host (billing-vm)               | `192.168.56.13`    |
| `RABBITMQ_USER`        | RabbitMQ user                            | `billing_rmq_user` |
| `RABBITMQ_PASSWORD`    | RabbitMQ password                        | `billing_rmq_password` |
| `BILLING_QUEUE`        | RabbitMQ queue name                      | `billing_queue`    |

## Setup & Run

```bash
# Clone the repository
git clone <repo-url>
cd crud-master

# Start all VMs (provisions on first run — takes ~5 minutes)
vagrant up

# Check VM status
vagrant status

# SSH into a VM
vagrant ssh inventory-vm
vagrant ssh gateway-vm
```

The API Gateway is forwarded to your host machine at **http://localhost:8080**.

## API Endpoints

All requests go through the **API Gateway** at `http://localhost:8080`.

### Inventory (Movies)

| Method   | Endpoint               | Description                          |
|----------|------------------------|--------------------------------------|
| `GET`    | `/api/movies`          | Get all movies                       |
| `GET`    | `/api/movies?title=X`  | Search movies by title               |
| `POST`   | `/api/movies`          | Create a new movie                   |
| `DELETE` | `/api/movies`          | Delete all movies                    |
| `GET`    | `/api/movies/<id>`     | Get a single movie by ID             |
| `PUT`    | `/api/movies/<id>`     | Update a movie by ID                 |
| `DELETE` | `/api/movies/<id>`     | Delete a movie by ID                 |

**Example: Create a movie**
```bash
curl -X POST http://localhost:8080/api/movies \
  -H "Content-Type: application/json" \
  -d '{"title": "Inception", "description": "A mind-bending thriller."}'
```

**Example: Get all movies**
```bash
curl http://localhost:8080/api/movies
```

**Example: Search by title**
```bash
curl "http://localhost:8080/api/movies?title=inception"
```

### Billing (disabled)

| Method | Endpoint       | Description                               |
|--------|----------------|-------------------------------------------|
| `POST` | `/api/billing` | Publish a billing message to RabbitMQ     |

> billing-vm is currently commented out in the Vagrantfile. The `/api/billing` endpoint will return 500 until billing-vm is enabled.

## Testing

A **Postman collection** is included at `postman_collection.json`. It covers all 7 inventory endpoints with automated test assertions.

**Import into Postman:**
1. Open Postman → Import → Upload `postman_collection.json`
2. Run the collection in order (POST first to create a movie, which sets the `movie_id` variable used by subsequent requests)

## PM2 Process Management

Inside each VM:

```bash
# List running processes
pm2 list

# Stop a service (e.g. to test resilience)
pm2 stop inventory-api
pm2 stop gateway-api

# Restart
pm2 start inventory-api
pm2 start gateway-api
```

## API Documentation

An **OpenAPI 3.0 specification** is available at `openapi.yaml`. You can visualize it using:
- [Swagger Editor](https://editor.swagger.io/) — paste the file contents
- VS Code with the OpenAPI extension

## Project Structure

```
.
├── .env                          # Environment variables (committed intentionally)
├── .gitignore
├── README.md
├── Vagrantfile                   # Defines inventory-vm + gateway-vm
├── openapi.yaml                  # OpenAPI 3.0 spec for the API Gateway
├── postman_collection.json       # Postman test collection
├── scripts/
│   ├── inventory.sh              # Provision script for inventory-vm
│   └── gateway.sh                # Provision script for gateway-vm
└── srcs/
    ├── inventory-app/
    │   ├── server.py         # Flask CRUD API
    │   └── requirements.txt
    └── api-gateway-app/
        ├── server.py         # Flask proxy + RabbitMQ publisher
        └── requirements.txt
```

## Design Choices

- **`server.py` inside `app/`**: The entry point lives in `app/` alongside other modules. PM2 is invoked from `$APP_DIR/app/` to keep the working directory consistent with module imports.
- **Single `.env` file**: All credentials are centralised and injected into VMs via Vagrant's `env:` provisioner option, so no credentials are hard-coded in source files.
- **PM2 in fork mode**: Python processes don't benefit from PM2's cluster mode, so fork mode is used. This is sufficient for process resilience and log management.