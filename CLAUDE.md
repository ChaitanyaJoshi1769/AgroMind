# AgroMind Development Context

## Project Overview

**AgroMind** is an AI-native agriculture operating system that combines:
- Real-time AI vision (plant-level weed/pest/disease detection)
- Autonomous robotics (tractors, drones, rovers)
- Biological intelligence (non-chemical crop protection)
- Predictive agronomy (yield/disease/pest forecasting)
- Edge AI (Jetson deployment for offline capability)
- Digital twins (GIS-based farm representation)

**Goal**: Reduce chemical usage by 90%+ while improving yields and soil health.

## Tech Stack

**Frontend**: Next.js 15 + React 19 + TypeScript + Tailwind CSS + Mapbox GL + Framer Motion
**Backend**: FastAPI + Node.js + PostgreSQL + TimescaleDB + Redis + Qdrant + Kafka
**AI/ML**: PyTorch + YOLOv11 + SAM + ONNX + TensorRT (Jetson)
**Robotics**: ROS2 + NVIDIA Isaac + PX4
**Infrastructure**: Docker + Kubernetes + Terraform + Prometheus + Grafana

## Monorepo Structure

```
/apps
  /web                # Next.js frontend dashboard
  /api                # FastAPI backend
  /edge-runtime       # Edge AI inference service
  /robotics-control   # ROS2 orchestration
  /vision-inference   # Vision model serving

/packages
  /ui                 # Shared React components
  /agronomy-engine    # Farming logic & agents
  /vision-core        # Vision models & utils
  /robotics-sdk       # Robotics interfaces
  /sensor-network     # IoT sensor management
  /digital-twin       # GIS & 3D visualization
  /ml-core            # Shared ML utilities
  /shared             # Common utilities

/infrastructure
  /kubernetes         # K8s manifests
  /terraform          # IaC for cloud
  /database           # SQL schemas
  /prometheus         # Monitoring
  /docker             # Dockerfiles
```

## Development Workflow

1. **Local Dev**: `npm run dev` spins up Docker Compose with all services
2. **Testing**: `npm run test` runs Jest + pytest
3. **Type Checking**: `npm run type-check` validates TypeScript
4. **CI/CD**: GitHub Actions auto-tests, builds, deploys

## Key Files

- `ARCHITECTURE.md` - System design (read first!)
- `README.md` - Quick start & feature overview
- `docker-compose.yml` - Local dev environment
- `apps/api/pyproject.toml` - Python dependencies
- `apps/web/package.json` - Frontend dependencies
- `infrastructure/database/init.sql` - Schema definition

## Database Schema

**Core Tables**:
- `farms` - Farm accounts
- `fields` - Individual fields within farms
- `zones` - Management units
- `assets` - Robots, drones, sensors
- `detections` - Vision system outputs
- `treatments` - Chemical/biological applications
- `sensor_metadata` - Sensor registry
- `predictions` - ML forecasts

**TimescaleDB** (Telemetry): High-cardinality time-series data
**Qdrant** (Vector DB): Semantic search for treatments/research

## API Patterns

**REST** (public): `/api/farms/`, `/api/telemetry/`, etc.
**gRPC** (internal): Vision, robotics, telemetry (real-time)
**WebSocket**: Live robot positions, detections

## Running Services

```bash
# Local everything
docker-compose up -d

# Just backend
cd apps/api && poetry run uvicorn src.main:app --reload

# Just frontend
cd apps/web && npm run dev

# Database migrations
cd apps/api && poetry run alembic upgrade head
```

## Common Tasks

**Add new API endpoint**: Create route in `apps/api/src/api/routes/`
**Add new React component**: Create in `apps/web/src/components/`
**Add new database table**: Update `infrastructure/database/init.sql`
**Deploy to K8s**: `kubectl apply -f infrastructure/kubernetes/`

## Performance Targets

- Vision latency: <100ms (edge), <50ms (optimized)
- Robot control latency: <50ms
- API p99: <200ms
- Telemetry ingestion: 1M events/sec
- Platform uptime: 99.9%

## Known Limitations (Phase 1)

- Vision models are placeholder (actual models need training data)
- Robotics integration is framework-only (needs hardware)
- Biological intelligence is recommendation engine (not ML-driven yet)
- Multi-tenant auth is scaffolding (needs implementation)
- GIS visualization is basic (needs advanced features)

## Next Steps

**Phase 2**: Precision spraying, robotics control, biological engine
**Phase 3**: Multi-agent systems, advanced predictions, DL training
**Phase 4**: Scalability, marketplace, enterprise deployment

## Contact

Built for agricultural sustainability. Questions? Check ARCHITECTURE.md or README.md.
