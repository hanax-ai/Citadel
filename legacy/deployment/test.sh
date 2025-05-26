
#!/usr/bin/env bash
# Script to run tests for Project Citadel

# Exit on error, undefined variables, and propagate errors in pipelines
set -euo pipefail

# Source common configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# Set up error trap
trap 'handle_error $LINENO' ERR

main() {
    log "Starting test process for Project Citadel"
    
    # Check if test directory exists
    check_test_dir
    
    # Check if source directory exists
    check_src_dir
    
    # Run the tests
    log "Running tests from ${TEST_DIR}"
    
    # Change to the test directory and run pytest
    cd "${TEST_DIR}"
    
    # Run pytest with verbose output
    if python -m pytest -v; then
        log "All tests passed successfully"
        return 0
    else
        TEST_EXIT_CODE=$?
        log "ERROR: Tests failed with exit code ${TEST_EXIT_CODE}"
        return ${TEST_EXIT_CODE}
    fi
}

# Run the main function and capture its exit code
main "$@"
exit $?
