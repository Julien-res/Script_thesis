def save_image(output_path, image_data, output_name):
    """Saves the processed image data to the specified output path."""
    from rasterio import open as rio_open
    with rio_open(f"{output_path}/{output_name}.jp2", 'w', driver='JP2OpenJPEG', height=image_data.shape[0],
                  width=image_data.shape[1], count=1, dtype=image_data.dtype) as dst:
        dst.write(image_data, 1)

def clear_cache(path):
    """Clears the __pycache__ directory in the specified path."""
    import os
    from glob import glob
    cache_files = glob(os.path.join(path, '__pycache__/*'))
    for f in cache_files:
        os.remove(f)