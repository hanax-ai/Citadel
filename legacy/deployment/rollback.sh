
#!/usr/bin/env bash
# Script to rollback to a previous version of Project Citadel

# Exit on error, undefined variables, and propagate errors in pipelines
set -euo pipefail

# Source common configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# Set up error trap
trap 'handle_error $LINENO' ERR

main() {
    local backup_path="$1"
    
    if [ -z "${backup_path}" ]; then
        # If no backup path is provided, use the most recent backup
        log "No backup path provided, finding most recent backup"
        backup_path=$(find "${BACKUP_DIR}" -name "citadel_backup_*.tar.gz" -type f -printf "%T@ %p\n" | sort -nr | head -1 | cut -d' ' -f2-)
        
        if [ -z "${backup_path}" ]; then
            log "ERROR: No backup files found in ${BACKUP_DIR}"
            exit 1
        fi
    fi
    
    log "Starting rollback process using backup: $(basename "${backup_path}")"
    
    # Check if backup file exists
    if [ ! -f "${backup_path}" ]; then
        log "ERROR: Backup file ${backup_path} does not exist"
        exit 1
    fi
    
    # Check if production directory exists
    if [ ! -d "${PROD_DIR}" ]; then
        log "Production directory does not exist, creating it"
        mkdir -p "$(dirname "${PROD_DIR}")"
    else
        log "Removing current production code"
        rm -rf "${PROD_DIR}"
    fi
    
    # Extract the backup
    log "Extracting backup to production directory"
    tar -xzf "${backup_path}" -C "$(dirname "${PROD_DIR}")" || {
        log "ERROR: Failed to extract backup"
        exit 1
    }
    
    log "Rollback completed successfully"
}

# Run the main function with the provided backup path (if any)
main "$@"
