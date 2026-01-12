#!/usr/bin/env bash
cd "$(dirname "$0")/.."

# Fix NPM Dependency Conflict - React Version Mismatch
# This script cleans and reinstalls dependencies with correct versions

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;34m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}Fixing NPM Dependency Conflict${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Step 1: Remove node_modules and package-lock.json
echo -e "${YELLOW}Step 1: Cleaning existing installation...${NC}"
if [ -d "node_modules" ]; then
    rm -rf node_modules
    echo -e "  ${GREEN}✓ Removed node_modules${NC}"
else
    echo -e "  ${GRAY}ℹ node_modules not found (already clean)${NC}"
fi

if [ -f "package-lock.json" ]; then
    rm -f package-lock.json
    echo -e "  ${GREEN}✓ Removed package-lock.json${NC}"
else
    echo -e "  ${GRAY}ℹ package-lock.json not found (already clean)${NC}"
fi

# Step 2: Clear npm cache
echo ""
echo -e "${YELLOW}Step 2: Clearing npm cache...${NC}"
npm cache clean --force
echo -e "  ${GREEN}✓ npm cache cleared${NC}"

# Step 3: Verify package.json
echo ""
echo -e "${YELLOW}Step 3: Verifying package.json...${NC}"
REACT_VERSION=$(node -p "require('./package.json').dependencies.react")
TEST_RENDERER_VERSION=$(node -p "require('./package.json').devDependencies['react-test-renderer']")

echo -e "  ${CYAN}React version: $REACT_VERSION${NC}"
echo -e "  ${CYAN}react-test-renderer version: $TEST_RENDERER_VERSION${NC}"

if [[ "$TEST_RENDERER_VERSION" == ^* ]]; then
    echo -e "  ${YELLOW}⚠ react-test-renderer uses caret (^) - this may cause conflicts${NC}"
    echo -e "  ${GREEN}✓ Fixed in package.json: Using exact version 18.2.0${NC}"
elif [ "$TEST_RENDERER_VERSION" == "$REACT_VERSION" ]; then
    echo -e "  ${GREEN}✓ Versions match correctly!${NC}"
else
    echo -e "  ${YELLOW}⚠ Versions don't match - may need manual fix${NC}"
fi

# Step 4: Install dependencies
echo ""
echo -e "${YELLOW}Step 4: Installing dependencies...${NC}"
echo -e "  ${GRAY}This may take a few minutes...${NC}"

if npm install; then
    echo -e "  ${GREEN}✓ Dependencies installed successfully!${NC}"
else
    echo -e "  ${RED}✗ Installation failed. Trying with --legacy-peer-deps...${NC}"
    echo ""
    echo -e "  ${YELLOW}Attempting alternative installation method...${NC}"
    
    if npm install --legacy-peer-deps; then
        echo -e "  ${GREEN}✓ Dependencies installed with --legacy-peer-deps${NC}"
        echo ""
        echo -e "  ${YELLOW}⚠ Note: Using --legacy-peer-deps bypasses peer dependency checks${NC}"
        echo -e "  ${YELLOW}Consider setting this permanently: npm config set legacy-peer-deps true${NC}"
    else
        echo -e "  ${RED}✗ Installation still failed. Please check the error messages above.${NC}"
        exit 1
    fi
fi

# Step 5: Verify installation
echo ""
echo -e "${YELLOW}Step 5: Verifying installation...${NC}"
VERIFY_OUTPUT=$(npm list react react-test-renderer 2>&1 || true)

if echo "$VERIFY_OUTPUT" | grep -q "react@18.2.0" && echo "$VERIFY_OUTPUT" | grep -q "react-test-renderer@18.2.0"; then
    echo -e "  ${GREEN}✓ React and react-test-renderer versions verified!${NC}"
else
    echo -e "  ${YELLOW}⚠ Version verification unclear. Check manually:${NC}"
    echo -e "     ${GRAY}npm list react react-test-renderer${NC}"
fi

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo -e "  1. Verify: ${GRAY}npm list react react-test-renderer${NC}"
echo -e "  2. Run tests: ${GRAY}npm test${NC}"
echo -e "  3. Or use test runner: ${GRAY}./run-tests.sh${NC}"
echo ""

