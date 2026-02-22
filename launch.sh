#!/bin/bash

# COCOA Launch Script - Terminal-Native ACE
# Beautiful startup sequence with dependency checking

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# ASCII Art
show_banner() {
    echo -e "${CYAN}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║            🧠 COCOA LAUNCHER - Terminal ACE v1.0                 ║"
    echo "║                   Artificial Cognitive Entity                    ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python() {
    if command_exists python3; then
        python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        major=$(echo $python_version | cut -d. -f1)
        minor=$(echo $python_version | cut -d. -f2)
        
        if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
            echo -e "  ✅ Python $python_version ${GREEN}(Compatible)${NC}"
            return 0
        else
            echo -e "  ❌ Python $python_version ${RED}(Needs 3.10+)${NC}"
            return 1
        fi
    else
        echo -e "  ❌ Python 3 ${RED}(Not installed)${NC}"
        return 1
    fi
}

# Check Docker
check_docker() {
    if command_exists docker; then
        if docker info >/dev/null 2>&1; then
            echo -e "  ✅ Docker ${GREEN}(Running)${NC}"
            return 0
        else
            echo -e "  ⚠️ Docker ${YELLOW}(Not running)${NC}"
            return 1
        fi
    else
        echo -e "  ❌ Docker ${RED}(Not installed)${NC}"
        return 1
    fi
}

# Start PostgreSQL container
start_database() {
    echo -e "${BLUE}Starting PostgreSQL with pgvector...${NC}"
    
    if docker-compose up -d postgres; then
        echo -e "  ✅ Database ${GREEN}(Started)${NC}"
        
        # Wait for database to be ready
        echo -e "  ${YELLOW}Waiting for database initialization...${NC}"
        for i in {1..30}; do
            if docker-compose exec -T postgres pg_isready -U cocoa -d cocoa >/dev/null 2>&1; then
                echo -e "  ✅ Database ${GREEN}(Ready)${NC}"
                return 0
            fi
            sleep 1
        done
        echo -e "  ⚠️ Database ${YELLOW}(Timeout, but may still work)${NC}"
        return 0
    else
        echo -e "  ❌ Database ${RED}(Failed to start)${NC}"
        return 1
    fi
}

# Setup virtual environment
setup_venv() {
    echo -e "${BLUE}Setting up Python environment...${NC}"
    
    if [ ! -d "venv_cocoa" ]; then
        python3 -m venv venv_cocoa
        echo -e "  ✅ Virtual environment ${GREEN}(Created)${NC}"
    else
        echo -e "  ✅ Virtual environment ${GREEN}(Exists)${NC}"
    fi
    
    # Activate virtual environment
    source venv_cocoa/bin/activate
    echo -e "  ✅ Virtual environment ${GREEN}(Activated)${NC}"
    
    # Install dependencies
    echo -e "  ${YELLOW}Installing Python dependencies...${NC}"
    if pip install -r requirements.txt >/dev/null 2>&1; then
        echo -e "  ✅ Dependencies ${GREEN}(Installed)${NC}"
        return 0
    else
        echo -e "  ❌ Dependencies ${RED}(Install failed)${NC}"
        return 1
    fi
}

# Check environment file
check_env() {
    if [ -f ".env" ]; then
        echo -e "  ✅ Environment ${GREEN}(Configured)${NC}"
        return 0
    else
        echo -e "  ⚠️ Environment ${YELLOW}(Creating template)${NC}"
        cp .env.example .env 2>/dev/null || {
            echo -e "  ❌ Environment ${RED}(.env.example missing)${NC}"
            return 1
        }
        echo -e "  ✅ Environment ${GREEN}(Template created)${NC}"
        echo -e "  ${YELLOW}Please edit .env with your API keys${NC}"
        return 0
    fi
}

# Main launcher function
launch_cocoa() {
    show_banner
    
    echo -e "${BOLD}🔍 System Check${NC}"
    
    # Check all dependencies
    python_ok=false
    docker_ok=false
    
    if check_python; then python_ok=true; fi
    if check_docker; then docker_ok=true; fi
    check_env
    
    echo ""
    
    # Start services
    if [ "$docker_ok" = true ]; then
        start_database
        echo ""
    else
        echo -e "${YELLOW}⚠️ Docker not available - COCOA will run with in-memory storage${NC}"
        echo ""
    fi
    
    # Setup Python environment
    if [ "$python_ok" = true ]; then
        if setup_venv; then
            echo ""
            echo -e "${BOLD}🚀 Launching COCOA...${NC}"
            echo ""
            
            # Launch COCOA
            source venv_cocoa/bin/activate
            python cocoa.py
        else
            echo -e "${RED}❌ Failed to setup Python environment${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Python 3.10+ is required to run COCOA${NC}"
        exit 1
    fi
}

# Handle command line arguments
case "$1" in
    "test")
        echo -e "${BLUE}Running COCOA system tests...${NC}"
        python test_cocoa.py
        ;;
    "db")
        echo -e "${BLUE}Starting database only...${NC}"
        docker-compose up postgres
        ;;
    "stop")
        echo -e "${YELLOW}Stopping COCOA services...${NC}"
        docker-compose down
        ;;
    "clean")
        echo -e "${YELLOW}Cleaning up COCOA environment...${NC}"
        docker-compose down -v
        rm -rf venv_cocoa
        echo -e "${GREEN}✅ Cleanup complete${NC}"
        ;;
    *)
        launch_cocoa
        ;;
esac