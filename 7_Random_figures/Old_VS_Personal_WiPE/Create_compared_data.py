import os
import re
import numpy as np
from osgeo import gdal

def extract_date_and_sequence(filename):
    match = re.search(r'(\d{2}[A-Z]{3}).*?(\d{8})', filename)
    if match:
        return match.group(1), match.group(2)
    return None, None

def process_images(path1, path2, output_path):
    print(f"Listing files in {path1} and {path2}...")
    files1 = os.listdir(path1)
    files2 = os.listdir(path2)

    print(f"Found {len(files1)} files in {path1}")
    print(f"Found {len(files2)} files in {path2}")

    for file1 in files1:
        date1, seq1 = extract_date_and_sequence(file1)
        if date1 and seq1:
            for file2 in files2:
                date2, seq2 = extract_date_and_sequence(file2)
                if date1 == date2 and seq1 == seq2:
                    print(f"Match : [Date: {date2}, Sequence: {seq2}]")
                    img1 = gdal.Open(os.path.join(path1, file1))
                    img2 = gdal.Open(os.path.join(path2, file2))
                    
                    if img1 is not None and img2 is not None:
                        output_filename1 = os.path.join(output_path, f'R1_{date1}_{seq1}.tif')
                        output_filename1 = os.path.join(output_path, f'R1_{date1}_{seq1}.tif')
                        # Check if region1 already exists
                        if os.path.exists(output_filename1):
                            print(f"File already exists, skipping processing: {output_filename1}")
                            continue
                        
                        # Save region2
                        output_filename2 = os.path.join(output_path, f'R2_{date1}_{seq1}.tif')
                        if os.path.exists(output_filename2):
                            print(f"File already exists, skipping processing: {output_filename2}")
                            continue
                        img1 = gdal.Open(os.path.join(path1, file1))
                        img2 = gdal.Open(os.path.join(path2, file2))
                        if img1 is not None and img2 is not None:
                            mask = img1.GetRasterBand(1).ReadAsArray()
                            data = img2.GetRasterBand(1).ReadAsArray()
                            # Replace 0s in data with -999 before masking for region2
                            data = np.where(data == 0, -999, data)
                            region1 = np.where(mask == 1, data, 0)
                            region2 = np.where(mask == 0, data, 0)
                            
                            driver = gdal.GetDriverByName('GTiff')
                            
                            # Create and save region1
                            out_ds1 = driver.Create(output_filename1, img1.RasterXSize, img1.RasterYSize, 1, gdal.GDT_Float32, ['COMPRESS=LZW'])
                            if out_ds1 is None:
                                print(f"Error: Could not create {output_filename1}")
                                break
                            out_ds1.GetRasterBand(1).WriteArray(region1)
                            out_ds1.SetGeoTransform(img1.GetGeoTransform())
                            out_ds1.SetProjection(img1.GetProjection())
                            out_ds1.FlushCache()
                            out_ds1 = None
                            
                            # Create and save region2
                            out_ds2 = driver.Create(output_filename2, img1.RasterXSize, img1.RasterYSize, 1, gdal.GDT_Float32, ['COMPRESS=LZW'])
                            if out_ds2 is None:
                                print(f"Error: Could not create {output_filename2}")
                                break
                            out_ds2.GetRasterBand(1).WriteArray(region2)
                            out_ds2.SetGeoTransform(img1.GetGeoTransform())
                            out_ds2.SetProjection(img1.GetProjection())
                            out_ds2.FlushCache()
                            out_ds2 = None
                        else:
                            print(f"Error: Could not open {file1} or {file2}")
                        break

if __name__ == "__main__":
    path1 = '/mnt/d/DATA/WiPE/Old_WiPE_2020/'
    path2 = '/mnt/d/DATA/WiPE/TREATED/'
    output_path = '/mnt/d/DATA/WiPE/Output/'
    
    print("Creating output directory if it doesn't exist...")
    os.makedirs(output_path, exist_ok=True)
    print("Starting image processing...")
    process_images(path1, path2, output_path)
    print("Processing complete.")