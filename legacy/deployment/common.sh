
#!/usr/bin/env bash
# Common configuration and utility functions for Project Citadel deployment scripts

# Configuration variables
SRC_DIR="/home/ubuntu/Citadel_Revisions/src/citadel"
PROD_DIR="/home/ubuntu/Citadel" # Production directory (assumed)
TEST_DIR="/home/ubuntu/Citadel_Revisions/tests"
BACKUP_DIR="/home/ubuntu/backups"
LOG_DIR="/home/ubuntu/Citadel_Revisions/deployment/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/deployment_${TIMESTAMP}.log"

# Create necessary directories
mkdir -p "${BACKUP_DIR}"
mkdir -p "${LOG_DIR}"

# Logging function
log() {
    local message="$1"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[${timestamp}] ${message}" | tee -a "${LOG_FILE}"
}

# Error handling function
handle_error() {
    local exit_code=$?
    local line_number=$1
    log "ERROR: Command failed at line ${line_number} with exit code ${exit_code}"
    exit ${exit_code}
}

# Check if production directory exists
check_prod_dir() {
    if [ ! -d "${PROD_DIR}" ]; then
        log "ERROR: Production directory ${PROD_DIR} does not exist"
        exit 1
    fi
}

# Check if source directory exists
check_src_dir() {
    if [ ! -d "${SRC_DIR}" ]; then
        log "ERROR: Source directory ${SRC_DIR} does not exist"
        exit 1
    fi
}

# Check if test directory exists
check_test_dir() {
    if [ ! -d "${TEST_DIR}" ]; then
        log "ERROR: Test directory ${TEST_DIR} does not exist"
        exit 1
    fi
}
