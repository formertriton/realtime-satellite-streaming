# 🛰️ Real-Time Satellite Telemetry & Threat Detection System

<img width="1356" height="839" alt="Screenshot 2025-10-28 232450" src="https://github.com/user-attachments/assets/43d641f4-2de3-47bf-9711-2f09917845e4" />

Advanced real-time streaming system for satellite telemetry processing, threat detection, and space situational awareness. Built with production-grade infrastructure using Kafka, TimescaleDB, and FastAPI.

## 🎯 Project Overview

This system demonstrates *enterprise-level real-time data streaming* capabilities for space operations, combining:

*🔴 Real-Time Data Streaming*: Kafka-based event streaming with sub-second latency
*🛰️ Satellite Telemetry Simulation*: Realistic orbital mechanics for 10+ satellites
*⚡ Event-Driven Architecture*: Asynchronous processing with WebSocket updates
*📊 Time-Series Database*: TimescaleDB for high-performance telemetry storage
*🚨 Threat Detection*: Real-time collision detection and anomaly identification
*🐳 Containerized Infrastructure*: Docker-based deployment for scalability
*📡 REST API*: FastAPI with real-time WebSocket streaming
*📈 Live Dashboard*: Interactive visualization of satellite positions and threats

## 🏗️ System Architecture
```
┌─────────────────┐
│   Satellite     │
│   Simulator     │──┐
└─────────────────┘  │
                     ▼
             ┌────────────┐
             │   Kafka    │
             │  Streaming │
             └────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   ┌────────┐  ┌────────┐  ┌────────┐
   │Threat  │  │Anomaly │  │ Data   │
   │Detector│  │Detector│  │ Store  │
   └────────┘  └────────┘  └────────┘
       │           │           │
       └───────────┼───────────┘
                   ▼
             ┌────────────┐
             │ TimescaleDB│
             │  PostgreSQL│
             └────────────┘
                    │
                    ▼
             ┌────────────┐
             │  FastAPI   │
             │ WebSocket  │
             └────────────┘
                    │
                    ▼
              ┌────────────┐
              │   Live     │
              │ Dashboard  │
              └────────────┘

```
## 🚀 Key Features
## Real-Time Streaming Infrastructure

*Apache Kafka*: Distributed event streaming with topic-based routing
*High Throughput*: Processes 1000+ messages/second
*Fault Tolerant*: Automatic failover and data replication
*Scalable*: Horizontal scaling with consumer groups

### Advanced Telemetry Processing

*Orbital Mechanics*: Realistic satellite position calculations using SGP4
*Multi-Satellite Tracking*: Simultaneous monitoring of 10+ satellites
*Position Updates*: Sub-second latency from generation to storage
*Data Enrichment*: Automatic calculation of derived metrics

### Threat Detection System

*Collision Detection*: Real-time proximity analysis between satellites
*Risk Assessment*: Probability-based threat scoring
*Anomaly Detection*: Statistical outlier identification
*Alert System*: Configurable thresholds and notifications

### Production-Ready Infrastructure

*Docker Compose*: Single-command infrastructure deployment
*TimescaleDB*: Optimized time-series data storage with automatic partitioning
*Redis*: Caching layer for high-performance queries
*Monitoring*: Prometheus metrics and health checks

### Backend & Streaming

*Python 3.9+*: Core application logic
*Apache Kafka*: Event streaming platform
*FastAPI*: Modern async web framework
*WebSockets*: Real-time bidirectional communication

### Data Storage

*PostgreSQL + TimescaleDB*: Time-series database
*Redis*: In-memory cache and pub/sub
*JSON*: Structured telemetry format

### Infrastructure

*Docker & Docker Compose*: Containerization
*Zookeeper*: Kafka coordination
*Uvicorn*: ASGI server

### Libraries & Tools

*Skyfield & SGP4*: Satellite orbital calculations
*NumPy & Pandas*: Data processing
*Loguru*: Structured logging
*Pydantic*: Data validation

## 🛠️ Installation

### Prerequisites
- Python 3.9 or higher
- Docker Desktop (for full infrastructure)
- Git
- 8GB RAM minimum (16GB recommended)

### Quick Start (Simulator Only)

```
# Clone repository
git clone https://github.com/formertriton/realtime-satellite-streaming.git
cd realtime-satellite-streaming
# Create virtual environment
python -m venv venv
.\\venv\\Scripts\\Activate.ps1

# Install dependencies
pip install numpy pandas scipy matplotlib skyfield sgp4 loguru python-dateutil pytz fastapi uvicorn pydantic python-dotenv

# Test simulator
python test\_simulator.py
```
### Full Infrastructure Setup (Docker Required)

```
# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📖 Usage

### Running the Satellite Simulator

```
# Basic test (30 seconds, 10 satellites)
python test\_simulator.py
# Direct simulation
python src/simulator/satellite\_simulator.py
```

### Streaming with Kafka (Requires Docker)

```
# Start infrastructure
docker-compose up -d

# Start producer (stream telemetry to Kafka)
python src/streaming/kafka\_producer.py --num-satellites 10 --interval 1.0

# Start consumer (process telemetry from Kafka)
python src/streaming/kafka\_consumer.py --group-id processor-1
```


## 📊 Sample Output
<img width="1229" height="236" alt="image" src="https://github.com/user-attachments/assets/063f90d0-0913-402b-9403-cc6448931833" />

<img width="1512" height="931" alt="Screenshot 2025-10-28 233309" src="https://github.com/user-attachments/assets/c8f4a1a6-fac0-48a1-9bdf-f4be366cb248" />


### Telemetry Data Point

```
{
"satellite\_id": 1,
"norad\_id": 25544,
"satellite\_name": "ISS",
"timestamp": "2025-10-29T06:20:27.730553+00:00",
"latitude": -9.467179,
"longitude": -7.59492,
"altitude\_km": 416.02,
velocity\_km\_s": 7.6704,
"x\_pos\_km": 6635.85,
"z\_pos\_km": -1116.35,
"vx\_km\_s": 1.6089,
"vy\_km\_s": 4.6584,
"vz\_km\_s": 5.8775,
"orbital\_period\_min": 92.74,
"inclination\_deg": 51.6,
"eccentricity": 0.0006
}
```
### Real-Time Streaming Output

```
[ISS            ] Alt=  420.3km  Lat=-51.39°  Lon=  97.01°  Vel=7.66km/s
[STARLINK-1600  ] Alt=  549.3km  Lat=  7.26°  Lon=   5.51°  Vel=7.59km/s
[FENGYUN-4A     ] Alt=35787.8km  Lat=  0.10°  Lon= 102.48°  Vel=3.07km/s
--- 30 total data points (3.0s elapsed) ---
```

### Software Engineering

*Distributed Systems*: Kafka-based event streaming architecture
*Microservices*: Decoupled producer/consumer pattern
*Asynchronous Programming*: Non-blocking I/O with async/await
*API Design*: RESTful endpoints with WebSocket streaming
*Containerization*: Docker multi-container orchestration

### Data Engineering

*Real-Time Processing*: Sub-second streaming pipelines
*Time-Series Data*: Optimized storage and querying
*Data Modeling*: Efficient schema design for telemetry
*ETL Pipelines*: Extract, transform, load workflows


### DevOps & Infrastructure

*Infrastructure as Code*: Docker Compose configurations
*Service Orchestration*: Multi-container dependencies
*Monitoring*: Health checks and metrics collection
*Scalability*: Horizontal scaling design patterns


### Domain Expertise

*Orbital Mechanics*: Satellite position calculations
*Space Operations*: Telemetry processing and threat detection
*Geospatial Analysis*: Coordinate transformations (ECI to lat/lon)
*Defense Applications*: Space situational awareness systems


## 📝 Project Structure

```
realtime-satellite-streaming/
├── src/
│   ├── simulator/              # Satellite telemetry generator
│   │   ├── satellite\_simulator.py
│   │   └── \_\_init\_\_.py
│   ├── streaming/              # Kafka producers/consumers
│   │   ├── kafka\_producer.py
│   │   ├── kafka\_consumer.py
│   │   └── \_\_init\_\_.py
│   ├── api/                    # FastAPI endpoints
│   ├── processors/             # Data processing logic
│   ├── database/               # Database models
│   └── dashboard/              # Web dashboard
├── docker/
│   └── init-db.sql            # Database initialization
├── config/                     # Configuration files
├── tests/                      # Unit and integration tests
├── data/                       # Generated telemetry data
├── docs/                       # Documentation
├── docker-compose.yml          # Infrastructure definition
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── test\_simulator.py           # Demo script
└── README.md
```

## 🤝 Contributing

This is a portfolio project showcasing real-time streaming architecture. Feedback and suggestions are welcome!

## 📄 License

MIT License - See LICENSE file for details

## 📧 Contact
*Angelo R.* - [@formertriton]

Built to demonstrate enterprise-level real-time data streaming, distributed systems, and space domain expertise for defense and aerospace applications.

## 🎯 Key Takeaways
This project demonstrates:

1. *Production-Ready Architecture*: Not just a toy project—uses industry-standard tools (Kafka, Docker, TimescaleDB)
2. *Real-Time Systems Expertise*: Sub-second latency streaming with fault tolerance
3. *Distributed Systems*: Event-driven microservices architecture
4. *Domain Knowledge*: Space operations + software engineering
5. *DevOps Skills*: Containerization, orchestration, infrastructure as code
6. *Scalability*: Designed for horizontal scaling and high availability

