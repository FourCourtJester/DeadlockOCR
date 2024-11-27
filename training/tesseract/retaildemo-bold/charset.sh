#!/bin/bash

# Output file name
output_file="charset.txt"

# Create the file with numbers from 1 to 500
for i in $(seq 1 500); do
  echo "${i}k" >> $output_file
done

echo "File $output_file created with numbers from 1 to 500."
