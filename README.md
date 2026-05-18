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
        │  RabbitMQ
        ▼
┌──────────────────┐
│   billing-vm     │
│ 192.168.56.13    │
│ RabbitMQ +       │
│ Billing consumer │
│ PostgreSQL       │
│ (billing_db)     │
└──────────────────┘
```

## Stack

| Component       | Technology                              |
|-----------------|-----------------------------------------|
| API Gateway     | Python 3, Flask, PM2                    |
| Inventory API   | Python 3, Flask, SQLAlchemy, PostgreSQL |
| Billing API     | Python 3, pika, SQLAlchemy, PostgreSQL  |
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
| `BILLING_VM_IP`        | IP of billing-vm                         | `192.168.56.13`    |
| `BILLING_DB_NAME`      | Billing PostgreSQL database name         | `billing_db`       |
| `BILLING_DB_USER`      | Billing PostgreSQL user                  | `billing_user`     |
| `BILLING_DB_PASSWORD`  | Billing PostgreSQL password              | `billing_password` |
| `BILLING_DB_HOST`      | DB host (inside billing-vm)              | `127.0.0.1`        |
| `BILLING_DB_PORT`      | Billing DB port                          | `5432`             |
| `RABBITMQ_HOST`        | RabbitMQ host (billing-vm)               | `192.168.56.13`    |
| `RABBITMQ_PORT`        | RabbitMQ AMQP port                       | `5672`             |
| `RABBITMQ_VHOST`       | RabbitMQ virtual host                    | `/`                |
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
vagrant ssh billing-vm
```

The API Gateway is forwarded to your host machine at **http://localhost:8080**.
RabbitMQ Management is forwarded at **http://localhost:15672** using the RabbitMQ credentials from `.env`.

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

### Billing

| Method | Endpoint       | Description                               |
|--------|----------------|-------------------------------------------|
| `POST` | `/api/billing` | Publish a billing message to RabbitMQ     |

**Example: Publish a billing order**
```bash
curl -X POST http://localhost:8080/api/billing \
  -H "Content-Type: application/json" \
  -d '{"user_id": "3", "number_of_items": "5", "total_amount": "180"}'
```

The gateway publishes the request body to RabbitMQ. The billing consumer stores it in the `orders` table in `billing_db`. If `billing-api` is stopped but RabbitMQ is running, the gateway still accepts requests and messages remain queued until the consumer starts again.

## Testing

A **Postman collection** is included at `postman_collection.json`. It covers all 7 inventory endpoints and the billing publish endpoint with automated test assertions.

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
pm2 stop billing-api

# Restart
pm2 start inventory-api
pm2 start gateway-api
pm2 start billing-api
```

To test billing resilience:

```bash
vagrant ssh billing-vm
pm2 stop billing-api
exit

curl -X POST http://localhost:8080/api/billing \
  -H "Content-Type: application/json" \
  -d '{"user_id": "3", "number_of_items": "5", "total_amount": "180"}'

vagrant ssh billing-vm
pm2 start billing-api
sudo -u postgres psql -d billing_db -c "SELECT * FROM orders;"
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
├── Vagrantfile                   # Defines inventory-vm + gateway-vm + billing-vm
├── openapi.yaml                  # OpenAPI 3.0 spec for the API Gateway
├── postman_collection.json       # Postman test collection
├── scripts/
│   ├── inventory.sh              # Provision script for inventory-vm
│   ├── gateway.sh                # Provision script for gateway-vm
│   └── billing.sh                # Provision script for billing-vm
└── srcs/
    ├── inventory-app/
    │   ├── server.py             # Flask CRUD API
    │   └── requirements.txt
    ├── api-gateway-app/
    │   ├── server.py             # Flask proxy + RabbitMQ publisher
    │   └── requirements.txt
    └── billing-app/
        ├── server.py             # RabbitMQ consumer + orders persistence
        └── requirements.txt
```

## Design Choices

- **Separate service directories**: Each service has its own `server.py` and `requirements.txt`, so it can be started manually with `python server.py` or managed by PM2 in its VM.
- **Single `.env` file**: All credentials are centralised and injected into VMs via Vagrant's `env:` provisioner option, so no credentials are hard-coded in source files.
- **PM2 in fork mode**: Python processes don't benefit from PM2's cluster mode, so fork mode is used. This is sufficient for process resilience and log management.
- **Queue-first billing**: The gateway only publishes billing messages to RabbitMQ. The Billing API has no HTTP endpoints and processes pending messages when it starts.
