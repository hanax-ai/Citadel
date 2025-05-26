#!/bin/bash

# Run integration tests for crawler implementations
cd /home/ubuntu/Citadel_Revisions
python -m pytest tests/integration/test_crawler_integration.py -v
