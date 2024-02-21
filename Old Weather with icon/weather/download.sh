#!/bin/bash

# List of image names
image_names=("01d.png" "01n.png" "02d.png" "02n.png" "03d.png" "03n.png" "04d.png" "04n.png" "09d.png" "09n.png" "10d.png" "10n.png" "11d.png" "11n.png" "13d.png" "13n.png" "50d.png" "50n.png")

# Base URL template
base_url="https://openweathermap.org/img/wn/"

# Directory to save the images
output_dir="weather_images"

# Create the output directory if it doesn't exist
mkdir -p "$output_dir"

# Loop through the image names and use wget to download each image
for image_name in "${image_names[@]}"; do
    wget -P "$output_dir" "${base_url}${image_name}"
done

echo "Download complete. Images are saved in the 'weather_images' directory."
