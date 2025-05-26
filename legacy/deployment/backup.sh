
#!/usr/bin/env bash
# Script to backup the existing Project Citadel code

# Exit on error, undefined variables, and propagate errors in pipelines
set -euo pipefail

# Source common configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# Set up error trap
trap 'handle_error $LINENO' ERR

main() {
    log "Starting backup process for Project Citadel"
    
    # Check if production directory exists
    check_prod_dir
    
    # Create backup filename with timestamp
    BACKUP_FILENAME="citadel_backup_${TIMESTAMP}.tar.gz"
    BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILENAME}"
    
    log "Creating backup at ${BACKUP_PATH}"
    
    # Create tar archive of the production directory
    tar -czf "${BACKUP_PATH}" -C "$(dirname "${PROD_DIR}")" "$(basename "${PROD_DIR}")" || {
        log "ERROR: Backup creation failed"
        exit 1
    }
    
    # Verify backup was created successfully
    if [ -f "${BACKUP_PATH}" ]; then
        BACKUP_SIZE=$(du -h "${BACKUP_PATH}" | cut -f1)
        log "Backup completed successfully: ${BACKUP_FILENAME} (${BACKUP_SIZE})"
        echo "${BACKUP_PATH}"  # Return the backup path for use by other scripts
    else
        log "ERROR: Backup file was not created"
        exit 1
    fi
}

# Run the main function
main "$@"
