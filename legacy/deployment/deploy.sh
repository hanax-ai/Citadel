
#!/usr/bin/env bash
# Main deployment script for Project Citadel

# Exit on error, undefined variables, and propagate errors in pipelines
set -euo pipefail

# Source common configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# Set up error trap
trap 'handle_error $LINENO' ERR

main() {
    log "Starting deployment process for Project Citadel"
    
    # Check if source directory exists
    check_src_dir
    
    # Check if production directory exists (or parent directory for creation)
    if [ ! -d "${PROD_DIR}" ]; then
        log "Production directory does not exist, creating it"
        mkdir -p "${PROD_DIR}"
    fi
    
    # Create backup before deployment
    log "Creating backup before deployment"
    BACKUP_PATH=$("${SCRIPT_DIR}/backup.sh")
    
    if [ $? -ne 0 ]; then
        log "ERROR: Backup failed, aborting deployment"
        exit 1
    fi
    
    log "Backup created successfully at ${BACKUP_PATH}"
    
    # Deploy new code
    log "Deploying new code from ${SRC_DIR} to ${PROD_DIR}"
    
    # Use rsync to copy files, preserving permissions and excluding version control
    rsync -av --delete --exclude=".git/" --exclude=".svn/" "${SRC_DIR}/" "${PROD_DIR}/" || {
        log "ERROR: Deployment failed"
        log "Rolling back to previous version"
        "${SCRIPT_DIR}/rollback.sh" "${BACKUP_PATH}"
        exit 1
    }
    
    # Run tests
    log "Running tests to verify deployment"
    if "${SCRIPT_DIR}/test.sh"; then
        log "Tests passed, deployment successful"
    else
        log "ERROR: Tests failed after deployment"
        log "Rolling back to previous version"
        "${SCRIPT_DIR}/rollback.sh" "${BACKUP_PATH}"
        exit 1
    fi
    
    log "Deployment completed successfully"
}

# Run the main function
main "$@"
