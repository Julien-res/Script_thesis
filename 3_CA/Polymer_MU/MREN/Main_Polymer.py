import os
import shutil
from polymer.main import run_atm_corr
from polymer.level1 import Level1
from polymer.level2 import Level2

def get_sentinel_files(input_path):
    """Retrieve Sentinel-2 files starting with S2A or S2B in a non-recursive manner."""
    return [f for f in os.listdir(input_path) if f.startswith(('S2A', 'S2B'))]

def read_or_create_file_list(input_path, txt_file):
    """Read or create a .txt file containing the list of Sentinel-2 files."""
    if os.path.exists(txt_file):
        with open(txt_file, 'r') as file:
            file_list = file.read().splitlines()
    else:
        file_list = get_sentinel_files(input_path)
        with open(txt_file, 'w') as file:
            file.write('\n'.join(file_list))
    return file_list

def find_granule_path(image_path):
    """Find the GRANULE directory inside a Sentinel-2 image folder."""
    granule_dir = os.path.join(image_path, 'GRANULE')
    if os.path.exists(granule_dir) and os.path.isdir(granule_dir):
        granules = os.listdir(granule_dir)
        if granules:
            return os.path.join(granule_dir, granules[0])  # Take the first GRANULE folder
    raise FileNotFoundError(f"No GRANULE directory found in {image_path}")

def apply_polymer_correction(granule_path, output_file):
    """Apply atmospheric correction using Polymer."""
    print(f"Applying Polymer correction to {granule_path}")
    run_atm_corr(
        Level1(granule_path),
        Level2(output_file),
        # Add any optional Polymer arguments here
    )
    return output_file

def process_images(input_path, output_path, txt_file):
    """Process Sentinel-2 images with Polymer correction."""
    file_list = read_or_create_file_list(input_path, txt_file)

    for image_name in file_list:
        image_path = os.path.join(input_path, image_name)
        if not os.path.exists(image_path):
            print(f"Image {image_name} not found, skipping...")
            continue

        try:
            # Find the GRANULE path
            granule_path = find_granule_path(image_path)

            # Define the output file path for Polymer
            output_file = os.path.join(output_path, f"{image_name}_corrected.nc")

            # Apply Polymer correction
            apply_polymer_correction(granule_path, output_file)

            print(f"Polymer correction applied and saved to {output_file}")

            # Remove the processed image from the list
            file_list.remove(image_name)
            with open(txt_file, 'w') as file:
                file.write('\n'.join(file_list))

            print(f"Processed and removed {image_name} from the list.")

        except Exception as e:
            print(f"Error processing {image_name}: {e}")

if __name__ == "__main__":
    # Input and output paths
    input_path = input("Enter the input path containing Sentinel-2 data: ").strip()
    output_path = input("Enter the output path for corrected images: ").strip()
    txt_file = "sentinel_file_list.txt"

    # Ensure output directory exists
    os.makedirs(output_path, exist_ok=True)

    # Process images
    process_images(input_path, output_path, txt_file)