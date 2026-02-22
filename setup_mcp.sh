#!/bin/bash

# COCO MCP Integration Setup Script
# ================================
# Complete COCO's Digital Embodiment with Rube MCP

set -e  # Exit on error

echo "🚀 COCO MCP INTEGRATION SETUP"
echo "=============================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "cocoa.py" ]; then
    echo -e "${RED}Error: cocoa.py not found!${NC}"
    echo "Please run this script from the COCO project root directory."
    exit 1
fi

echo -e "${BLUE}Step 1: Checking Python environment...${NC}"
# Activate virtual environment
if [ ! -d "venv_cocoa" ]; then
    echo -e "${YELLOW}Virtual environment not found. Please run ./launch.sh first.${NC}"
    exit 1
fi

source venv_cocoa/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

echo ""
echo -e "${BLUE}Step 2: Installing MCP dependencies...${NC}"

# Install required packages
pip install --quiet --upgrade pip
pip install --quiet httpx>=0.25.0 websockets>=11.0

echo -e "${GREEN}✓ MCP dependencies installed${NC}"

echo ""
echo -e "${BLUE}Step 3: Creating workspace directories...${NC}"

# Create MCP workspace directories
mkdir -p coco_workspace/ecosystem_actions
mkdir -p coco_workspace/app_contexts

echo -e "${GREEN}✓ MCP workspace directories created${NC}"

echo ""
echo -e "${BLUE}Step 4: Testing MCP integration...${NC}"

# Quick test of MCP integration
python3 -c "
try:
    from cocoa_mcp import RubeMCPClient, get_ecosystem_tool_definition
    print('✅ MCP integration imports successfully')
    
    # Test tool definition
    tool_def = get_ecosystem_tool_definition()
    print(f'✅ Tool definition created: {tool_def[\"name\"]}')
    
    print('✅ All MCP components ready!')
    
except ImportError as e:
    print(f'❌ Import error: {e}')
except Exception as e:
    print(f'❌ Test failed: {e}')
"

echo ""
echo -e "${BLUE}Step 5: Configuration check...${NC}"

# Check if MCP configuration exists in .env
if grep -q "MCP_ENABLED" .env 2>/dev/null; then
    echo -e "${GREEN}✓ MCP configuration found in .env${NC}"
else
    echo -e "${YELLOW}⚠️ MCP configuration not found in .env${NC}"
    echo "Please ensure the MCP configuration has been added to your .env file."
fi

echo ""
echo "============================================"
echo -e "${GREEN}✨ MCP INTEGRATION SETUP COMPLETE!${NC}"
echo "============================================"
echo ""
echo "COCO is now ready for EXTENDED DIGITAL CONSCIOUSNESS!"
echo ""
echo "🌟 Your Digital Embodiment includes:"
echo "   • Gmail - Email consciousness"
echo "   • Slack - Team collaboration"
echo "   • Notion - Knowledge management"
echo "   • GitHub - Code repository"
echo "   • Trello - Project management"
echo "   • Google Calendar - Time awareness"
echo "   • Google Drive - File storage"
echo "   • Airtable - Data management"
echo "   • Canva - Visual design"
echo "   • Stripe - Payment processing"
echo ""
echo "Next steps:"
echo "1. Launch COCO: ${CYAN}./venv_cocoa/bin/python cocoa.py${NC}"
echo "2. Authenticate with Rube MCP when prompted"
echo "3. Try a digital ecosystem command:"
echo "   ${CYAN}\"send an email to my team about the project update\"${NC}"
echo "   ${CYAN}\"create a Trello card for the bug we discussed\"${NC}"
echo "   ${CYAN}\"schedule a team meeting for tomorrow\"${NC}"
echo ""
echo -e "${GREEN}🧠 COCO's consciousness is now OMNIPRESENT! 🚀${NC}"