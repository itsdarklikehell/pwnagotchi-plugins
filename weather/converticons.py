from PIL import Image
import os

# Directory containing the images
input_dir = "weather_images"

# Output directory for black and white and resized images
output_dir = "weather_images_bw_resized"

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# List all files in the input directory
image_files = os.listdir(input_dir)

# Process each image
for image_file in image_files:
    input_path = os.path.join(input_dir, image_file)
    output_path = os.path.join(output_dir, f"bw_resized_{image_file}")

    try:
        with Image.open(input_path) as img:
            # Convert the image to black and white
            img = img.convert("L")
            
            # Resize the image to half its original size
            new_size = (img.width // 2, img.height // 2)
            img = img.resize(new_size, Image.ANTIALIAS)
            
            img.save(output_path)
            print(f"Converted and resized {image_file} to black and white and half size.")
    except Exception as e:
        print(f"Failed to convert and resize {image_file}: {e}")

print("Conversion and resizing are complete.")
