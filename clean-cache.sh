#!/bin/sh
max_age=2592000 # thirty days
for file in ~/.phenny/cache/*; do
  then=$( stat -c "%Y" "$file" )
  age=$( date -d "now - $then seconds" +%s )
  if [ $age -gt $max_age ]; then
    rm "$file"
  fi
done
