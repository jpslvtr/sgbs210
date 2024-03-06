#!/bin/bash
for file in data_ais/*.json; do
  echo "Formatting $file"
  npx prettier --write "$file"
done
