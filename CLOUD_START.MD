# 1. Start all services
```bash
docker compose -f docker-compose.cloud.yml up -d
```

# 2. Wait for services to be ready (about 1-2 minutes)
# 3. Access your platform!

# View all services
```bash
docker compose -f docker-compose.cloud.yml ps
```
# View logs
```bash
docker compose -f docker-compose.cloud.yml logs [service-name]
```
# Stop all services
```bash
docker compose -f docker-compose.cloud.yml down
```
# Restart a specific service
```bash
docker compose -f docker-compose.cloud.yml restart [service-name]
```
# Rebuild and restart
```bash
docker compose -f docker-compose.cloud.yml up -d --build
```