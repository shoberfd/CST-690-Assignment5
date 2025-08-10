# Enterprise Inventory Bot

This project provides a comprehensive monitoring, maintenance, and ROI strategy for a Python-based inventory bot. The solution uses a modern infrastructure stack to provide observability and scalability.

***

## Project Structure

- `inventory_bot.py`: The core Python script that runs the bot, generates metrics, and handles logging.
- `docs/`: Contains the project's documentation, including the monitoring, maintenance, and ROI plans in Markdown format.
- `docker-compose.yml`: Defines the Docker services for Prometheus and Grafana.
- `prometheus.yml`: The configuration file for the Prometheus server.

***

## Getting Started

Follow these steps to set up and run the entire monitoring stack on your local machine.

### 1. Install Dependencies

First, install the necessary Python libraries for the bot to run.

```bash
pip install -r requirements.txt
```

### 2. Run the Monitoring Stack

Open two separate terminal windows.

Terminal 1: Run the Inventory Bot

Start your Python script to begin generating metrics and logs. This will also start the Prometheus client's HTTP server on port 9100.
```bash
python inventory_bot.py
```
Terminal 2: Run Docker Compose

Start the Prometheus and Grafana containers. Docker Compose will handle the networking, allowing them to communicate.
```bash
docker-compose up -d
```
### 3. Access the Dashboards

- Prometheus UI: Open your browser and go to http://localhost:9090.
- Grafana UI: Open your browser and go to http://localhost:3000. Log in with the default credentials (admin/admin) and follow the steps to connect Grafana to your Prometheus server at the URL http://prometheus:9090.
