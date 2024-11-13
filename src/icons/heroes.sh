#!/bin/bash

# Get the latest JSON data
json_data=$(curl -s "https://assets.deadlock-api.com/v2/heroes?only_active=true")

# Extract each icon URL and download it
echo "$json_data" | jq -r '.[].images.icon_hero_card_webp' | while read -r image; do
    # Extract the icon name from the URL
    image_name="${image/card_psd/vertical_psd}"
    icon_name=$(basename "$image_name")

    # Download the icon and save it to the folder
    curl -s "$image_name" -o "./heroes/${icon_name/_vertical_psd/}"

    echo "Downloaded: $image_name"
done

echo "All icons downloaded successfully."
