#!/bin/bash

# AI Agents Data and Logs Repository Validation Script
# This script validates the structure and content of the repository

echo "🔍 AI Agents Data and Logs Repository Validation"
echo "=================================================="

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
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

echo "📁 Checking directory structure..."

# Check main directories
directories=("data" "logs" "agents" "provenance" "receipts" "compliance" "audit" "docs")
for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        log_test 0 "Directory '$dir' exists"
    else
        log_test 1 "Directory '$dir' missing"
    fi
done

# Check subdirectories
subdirs=(
    "data/raw" "data/processed" "data/schemas" "data/exports"
    "logs/access" "logs/audit" "logs/error" "logs/performance"
    "agents/configs" "agents/manifests" "agents/templates" "agents/runtime"
    "provenance/chains" "provenance/lineage" "provenance/metadata"
    "receipts/transactions" "receipts/operations" "receipts/completions"
    "compliance/policies" "compliance/reports" "compliance/certifications"
    "audit/trails" "audit/reviews" "audit/assessments"
)

for subdir in "${subdirs[@]}"; do
    if [ -d "$subdir" ]; then
        log_test 0 "Subdirectory '$subdir' exists"
    else
        log_test 1 "Subdirectory '$subdir' missing"
    fi
done

echo ""
echo "📄 Checking core documentation files..."

# Check core files
core_files=("README.md" "CONTRIBUTING.md" "docs/ORCHESTRATION_AND_COMPLIANCE.md")
for file in "${core_files[@]}"; do
    if [ -f "$file" ]; then
        log_test 0 "Core file '$file' exists"
    else
        log_test 1 "Core file '$file' missing"
    fi
done

echo ""
echo "🔧 Checking sample configuration files..."

# Check sample files
sample_files=(
    "agents/manifests/data-processing-agent.yaml"
    "agents/manifests/agent-registry.json"
    "agents/templates/agent-config-template.yaml"
    "agents/configs/ml-training-agent-config.json"
    "data/schemas/agent-manifest-schema.json"
    "data/schemas/receipt-schema.json"
)

for file in "${sample_files[@]}"; do
    if [ -f "$file" ]; then
        log_test 0 "Sample file '$file' exists"
    else
        log_test 1 "Sample file '$file' missing"
    fi
done

echo ""
echo "🧾 Checking receipt examples..."

# Check receipt files
receipt_files=(
    "receipts/operations/ml-training-receipt-20241219.json"
    "receipts/transactions/api-service-call-receipt-20241219.json"
    "receipts/completions/workflow-completion-certificate-20241219.json"
)

for file in "${receipt_files[@]}"; do
    if [ -f "$file" ]; then
        log_test 0 "Receipt file '$file' exists"
    else
        log_test 1 "Receipt file '$file' missing"
    fi
done

echo ""
echo "📋 Checking compliance and audit files..."

# Check compliance files
compliance_files=(
    "compliance/policies/data-governance-policy.md"
    "audit/trails/comprehensive-audit-trail-20241219.json"
    "provenance/lineage/sentiment-model-v2.3-lineage.json"
    "provenance/chains/customer-onboarding-workflow-provenance.json"
)

for file in "${compliance_files[@]}"; do
    if [ -f "$file" ]; then
        log_test 0 "Compliance file '$file' exists"
    else
        log_test 1 "Compliance file '$file' missing"
    fi
done

echo ""
echo "📊 Checking log files..."

# Check log files
log_files=(
    "logs/audit/ml-training-audit-20241219.jsonl"
)

for file in "${log_files[@]}"; do
    if [ -f "$file" ]; then
        log_test 0 "Log file '$file' exists"
    else
        log_test 1 "Log file '$file' missing"
    fi
done

echo ""
echo "🔍 Validating JSON files..."

# Function to validate JSON
validate_json() {
    if command -v jq >/dev/null 2>&1; then
        if jq empty "$1" >/dev/null 2>&1; then
            log_test 0 "JSON file '$1' is valid"
        else
            log_test 1 "JSON file '$1' has invalid syntax"
        fi
    else
        if python3 -m json.tool "$1" >/dev/null 2>&1; then
            log_test 0 "JSON file '$1' is valid (validated with Python)"
        else
            log_test 1 "JSON file '$1' has invalid syntax"
        fi
    fi
}

# Find and validate all JSON files
find . -name "*.json" -type f | while read -r json_file; do
    validate_json "$json_file"
done

echo ""
echo "📈 Validation Summary"
echo "===================="
echo -e "Total checks: ${TOTAL_CHECKS}"
echo -e "${GREEN}Passed: ${PASSED_CHECKS}${NC}"
echo -e "${RED}Failed: ${FAILED_CHECKS}${NC}"

if [ $FAILED_CHECKS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 All validations passed! Repository structure is complete.${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}⚠️  Some validations failed. Please check the missing files or issues.${NC}"
    exit 1
fi