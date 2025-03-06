import os
import re
from osgeo import gdal

def extract_date_and_sequence(filename):
    match = re.search(r'(\d{8})_.*?(\d{2}[A-Z]{3})', filename)
    if match:
        return match.group(1), match.group(2)
    return None, None

def process_images(path1, path2, output_path):
    files1 = os.listdir(path1)
    files2 = os.listdir(path2)

    for file1 in files1:
        date1, seq1 = extract_date_and_sequence(file1)
        if date1 and seq1:
            for file2 in files2:
                date2, seq2 = extract_date_and_sequence(file2)
                if date1 == date2 and seq1 == seq2:
                    img1 = gdal.Open(os.path.join(path1, file1))
                    img2 = gdal.Open(os.path.join(path2, file2))
                    
                    if img1 is not None and img2 is not None:
                        band1 = img1.GetRasterBand(1).ReadAsArray()
                        band2 = img2.GetRasterBand(1).ReadAsArray()
                        
                        result = band1 - band2
                        
                        driver = gdal.GetDriverByName('GTiff')
                        output_filename = os.path.join(output_path, f'result_{date1}_{seq1}.tif')
                        out_ds = driver.Create(output_filename, img1.RasterXSize, img1.RasterYSize, 1, gdal.GDT_Float32)
                        out_ds.GetRasterBand(1).WriteArray(result)
                        out_ds.SetGeoTransform(img1.GetGeoTransform())
                        out_ds.SetProjection(img1.GetProjection())
                        out_ds.FlushCache()
                        out_ds = None
                    break

if __name__ == "__main__":
    path1 = 'path/to/first/mask/folder'
    path2 = 'path/to/second/mask/folder'
    output_path = 'path/to/output/folder'
    
    process_images(path1, path2, output_path)