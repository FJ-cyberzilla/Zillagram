#!/bin/bash
# deploy.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Enterprise OSINT Platform Deployment${NC}"

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}⚠️  No .env file found, using defaults${NC}"
fi

ENVIRONMENT=${1:-production}
DOCKER_COMPOSE_FILE="docker-compose.$ENVIRONMENT.yml"

if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
    echo -e "${RED}❌ Docker compose file $DOCKER_COMPOSE_FILE not found${NC}"
    exit 1
fi

echo -e "${GREEN}📦 Building Docker images...${NC}"
docker-compose -f $DOCKER_COMPOSE_FILE build

echo -e "${GREEN}🔧 Starting services...${NC}"
docker-compose -f $DOCKER_COMPOSE_FILE up -d

echo -e "${GREEN}⏳ Waiting for services to be healthy...${NC}"
sleep 30

# Health checks
echo -e "${GREEN}🏥 Performing health checks...${NC}"

# Check API Gateway
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API Gateway is healthy${NC}"
else
    echo -e "${RED}❌ API Gateway health check failed${NC}"
    exit 1
fi

# Check database
if docker-compose -f $DOCKER_COMPOSE_FILE exec -T postgres pg_isready -U osint_user -d osint_platform > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Database is healthy${NC}"
else
    echo -e "${RED}❌ Database health check failed${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${BLUE}📊 Access URLs:${NC}"
echo -e "   API: http://localhost:8080"
echo -e "   API Docs: http://localhost:8080/docs"
echo -e "   Monitoring: http://localhost:3000"
echo -e "   Metrics: http://localhost:9090"
