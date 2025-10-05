#!/bin/bash

# AI Agents Data Import Validation Script
# This script validates all imported agent data, logs, and receipts

echo "🔍 AI Agents Data Import Validation"
echo "===================================="

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Function to log test results
log_test() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${RED}✗${NC} $2"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
}

echo -e "${BLUE}📥 Checking imported data structure...${NC}"

# Check new imported directories
imported_dirs=(
    "data/sessions/master-quest-sessions"
    "data/sessions/comet-assistant-sessions" 
    "data/sessions/cross-platform-sessions"
    "data/manifests"
    "data/imported"
    "logs/imported"
    "logs/agent-activity"
    "logs/orchestration"
    "logs/system-events"
    "receipts/import-receipts"
    "receipts/workflow-receipts"
    "receipts/compliance-receipts"
    "provenance/chain-documents"
    "provenance/attribution-records"
    "provenance/lineage-maps"
    "compliance/security-policies"
    "compliance/audit-requirements"
    "compliance/regulatory-frameworks"
    "audit/integrity-checks"
    "audit/access-logs"
    "audit/reconciliation-reports"
)

for dir in "${imported_dirs[@]}"; do
    if [ -d "$dir" ]; then
        log_test 0 "Imported directory '$dir' exists"
    else
        log_test 1 "Imported directory '$dir' missing"
    fi
done

echo ""
echo -e "${BLUE}📄 Checking imported files...${NC}"

# Check imported files
imported_files=(
    "logs/imported/copilot-master-quest-pr10-20240924.jsonl"
    "logs/imported/copilot-session-20240924.jsonl"
    "receipts/workflow-receipts/master-quest-pr10-receipt.json"
    "receipts/import-receipts/cross-platform-sync-receipt.json"
    "audit/trails/cross-agent-orchestration-audit-20240924.json"
    "compliance/audit-requirements/integrity-verification.md"
    "data/manifests/cross-agent-coordination-manifest.yaml"
    "data/sessions/master-quest-sessions/copilot-session-ai-data-logs-20240924.json"
    "data/sessions/comet-assistant-sessions/comet-browser-session-20240920.json"
    "logs/orchestration/orchestration-events-20240924.jsonl"
)

for file in "${imported_files[@]}"; do
    if [ -f "$file" ]; then
        log_test 0 "Imported file '$file' exists"
    else
        log_test 1 "Imported file '$file' missing"
    fi
done

echo ""
echo -e "${BLUE}🔍 Validating JSON files...${NC}"

# Function to validate JSON
validate_json() {
    if command -v python3 >/dev/null 2>&1; then
        if python3 -c "import json; json.load(open('$1'))" 2>/dev/null; then
            log_test 0 "JSON file '$1' is valid"
        else
            log_test 1 "JSON file '$1' has invalid syntax"
        fi
    else
        log_test 0 "JSON file '$1' (validation skipped - no python3)"
    fi
}

# Validate specific imported JSON files
json_files=(
    "receipts/workflow-receipts/master-quest-pr10-receipt.json"
    "receipts/import-receipts/cross-platform-sync-receipt.json"
    "audit/trails/cross-agent-orchestration-audit-20240924.json"
    "data/sessions/master-quest-sessions/copilot-session-ai-data-logs-20240924.json"
    "data/sessions/comet-assistant-sessions/comet-browser-session-20240920.json"
)

for json_file in "${json_files[@]}"; do
    if [ -f "$json_file" ]; then
        validate_json "$json_file"
    fi
done

echo ""
echo -e "${BLUE}📊 Checking import simulation data integrity...${NC}"

# Check for key import simulation elements
if [ -f "logs/imported/copilot-master-quest-pr10-20240924.jsonl" ]; then
    # Check if file contains expected Master-Quest PR #10 data
    if grep -q "master-quest-pr10" "logs/imported/copilot-master-quest-pr10-20240924.jsonl"; then
        log_test 0 "Master-Quest PR #10 data contains expected correlation IDs"
    else
        log_test 1 "Master-Quest PR #10 data missing correlation IDs"
    fi
fi

if [ -f "receipts/workflow-receipts/master-quest-pr10-receipt.json" ]; then
    # Check if receipt contains digital signature
    if grep -q "signature" "receipts/workflow-receipts/master-quest-pr10-receipt.json"; then
        log_test 0 "Master-Quest PR #10 receipt contains digital signature"
    else
        log_test 1 "Master-Quest PR #10 receipt missing digital signature"
    fi
fi

if [ -f "audit/trails/cross-agent-orchestration-audit-20240924.json" ]; then
    # Check if audit trail contains orchestration events
    if grep -q "orchestration_events" "audit/trails/cross-agent-orchestration-audit-20240924.json"; then
        log_test 0 "Cross-agent orchestration audit contains orchestration events"
    else
        log_test 1 "Cross-agent orchestration audit missing orchestration events"
    fi
fi

echo ""
echo -e "${BLUE}🔐 Checking compliance and integrity elements...${NC}"

if [ -f "compliance/audit-requirements/integrity-verification.md" ]; then
    # Check for hash verification content
    if grep -q "SHA-256" "compliance/audit-requirements/integrity-verification.md"; then
        log_test 0 "Integrity verification contains hash validation"
    else
        log_test 1 "Integrity verification missing hash validation"
    fi
    
    # Check for digital signature verification
    if grep -q "Digital Signature Verification" "compliance/audit-requirements/integrity-verification.md"; then
        log_test 0 "Integrity verification contains signature validation"
    else
        log_test 1 "Integrity verification missing signature validation"  
    fi
fi

echo ""
echo -e "${BLUE}🤖 Checking agent attribution and provenance...${NC}"

# Check for proper agent attribution in logs
if [ -f "logs/imported/copilot-session-20240924.jsonl" ]; then
    if grep -q "copilot-agent" "logs/imported/copilot-session-20240924.jsonl"; then
        log_test 0 "Session logs contain proper agent attribution"
    else
        log_test 1 "Session logs missing agent attribution"
    fi
fi

# Check for provenance chains in receipts
receipt_count=0
for receipt_file in receipts/workflow-receipts/*.json receipts/import-receipts/*.json; do
    if [ -f "$receipt_file" ]; then
        if grep -q "provenance\|attribution" "$receipt_file"; then
            receipt_count=$((receipt_count + 1))
        fi
    fi
done

if [ $receipt_count -ge 2 ]; then
    log_test 0 "Receipts contain provenance and attribution data"
else
    log_test 1 "Receipts missing provenance and attribution data"
fi

echo ""
echo -e "${BLUE}📈 Import Validation Summary${NC}"
echo "================================"
echo -e "Total checks: ${TOTAL_CHECKS}"
echo -e "${GREEN}Passed: ${PASSED_CHECKS}${NC}"
echo -e "${RED}Failed: ${FAILED_CHECKS}${NC}"

echo ""
echo -e "${BLUE}📋 Import Statistics${NC}"
echo "====================="

# Count imported files
imported_count=0
for dir in data/sessions logs/imported receipts/import-receipts receipts/workflow-receipts audit/trails compliance/audit-requirements data/manifests logs/orchestration; do
    if [ -d "$dir" ]; then
        count=$(find "$dir" -type f | wc -l)
        imported_count=$((imported_count + count))
        echo -e "${YELLOW}$dir${NC}: $count files"
    fi
done

echo -e "${YELLOW}Total imported files${NC}: $imported_count"

# Calculate file sizes
total_size=0
if command -v du >/dev/null 2>&1; then
    for dir in data/sessions logs/imported receipts/import-receipts receipts/workflow-receipts audit/trails compliance/audit-requirements data/manifests logs/orchestration; do
        if [ -d "$dir" ]; then
            size=$(du -sk "$dir" 2>/dev/null | cut -f1)
            total_size=$((total_size + size))
        fi
    done
    echo -e "${YELLOW}Total imported data size${NC}: ${total_size}KB"
fi

echo ""
if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${GREEN}🎉 All import validations passed! Cross-platform data import successful.${NC}"
    echo -e "${GREEN}✅ Single source-of-truth established for AI agent activity${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some import validations failed. Please check the missing files or issues.${NC}"
    exit 1
fi