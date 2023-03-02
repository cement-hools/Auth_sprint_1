#!/usr/bin/env bash
functional/utils/wait-for-it.sh elasticsearch:9200 --timeout=30 --strict -- \
  functional/utils/wait-for-it.sh redis:6379 --timeout=10 --strict -- \
  functional/utils/wait-for-it.sh async_api:8000 --timeout=10 --strict -- \
  functional/utils/wait-for-it.sh nginx:80 --timeout=10 --strict -- \
  python -m pytest .