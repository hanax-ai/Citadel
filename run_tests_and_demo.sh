
#!/bin/bash

# Run tests and demo for Project Citadel
# This script runs all tests and the full demo to verify that everything is working correctly

# Set up colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running Project Citadel Tests and Demo${NC}"
echo "========================================"

# Install the package in development mode
echo -e "${YELLOW}Installing package in development mode...${NC}"
pip install -e .
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install package${NC}"
    exit 1
fi
echo -e "${GREEN}Package installed successfully${NC}"
echo

# Run the reasoning tests
echo -e "${YELLOW}Running reasoning tests...${NC}"
python -m pytest tests/test_reasoning.py -v
if [ $? -ne 0 ]; then
    echo -e "${RED}Reasoning tests failed${NC}"
    exit 1
fi
echo -e "${GREEN}Reasoning tests passed${NC}"
echo

# Run the team coordination tests
echo -e "${YELLOW}Running team coordination tests...${NC}"
python -m pytest tests/test_team.py -v
if [ $? -ne 0 ]; then
    echo -e "${RED}Team coordination tests failed${NC}"
    exit 1
fi
echo -e "${GREEN}Team coordination tests passed${NC}"
echo

# Run the memory tests
echo -e "${YELLOW}Running memory tests...${NC}"
python -m pytest tests/test_memory.py -v
if [ $? -ne 0 ]; then
    echo -e "${RED}Memory tests failed${NC}"
    exit 1
fi
echo -e "${GREEN}Memory tests passed${NC}"
echo

# Run the feedback tests
echo -e "${YELLOW}Running feedback tests...${NC}"
python -m pytest tests/test_feedback.py -v
if [ $? -ne 0 ]; then
    echo -e "${RED}Feedback tests failed${NC}"
    exit 1
fi
echo -e "${GREEN}Feedback tests passed${NC}"
echo

# Run the enhanced agent tests
echo -e "${YELLOW}Running enhanced agent tests...${NC}"
python -m pytest tests/test_enhanced_agent.py -v
if [ $? -ne 0 ]; then
    echo -e "${RED}Enhanced agent tests failed${NC}"
    exit 1
fi
echo -e "${GREEN}Enhanced agent tests passed${NC}"
echo

# Run the full demo
echo -e "${YELLOW}Running full demo...${NC}"
python examples/full_demo.py
if [ $? -ne 0 ]; then
    echo -e "${RED}Full demo failed${NC}"
    exit 1
fi
echo -e "${GREEN}Full demo completed successfully${NC}"
echo

echo -e "${GREEN}All tests and demo completed successfully!${NC}"
echo "Project Citadel is ready for use."
