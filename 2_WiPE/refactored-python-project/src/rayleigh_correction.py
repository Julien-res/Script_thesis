class RayleighCorrection:
    def __init__(self, input_path, target_res=20, band="B2", resolution_method="Sampling"):
        self.input_path = input_path
        self.target_res = target_res
        self.band = band
        self.resolution_method = resolution_method
        self.product = None

    def load_product(self):
        from esa_snappy import ProductIO
        self.product = ProductIO.readProduct(self.input_path)
        if self.product is None:
            raise RuntimeError("Error: Sentinel-2 product could not be loaded. Check the input path.")
        print(f"Product loaded: {self.product.getName()}")

    def apply_rayleigh_correction(self):
        from esa_snappy import HashMap, GPF
        if self.product is None:
            self.load_product()

        parameters = HashMap()
        parameters.put('sourceBandNames', self.band)
        parameters.put('computeRBrr', 'true')

        resolutions = {
            "B2": 10, "B3": 10, "B4": 10,
            "B7": 20, "B10": 60, "B11": 20, "B12": 20
        }
        res = resolutions.get(self.band, 60)
        parameters.put('s2MsiTargetResolution', res if self.resolution_method == "Sampling" else 20)

        corrected_product = GPF.createProduct("RayleighCorrection", parameters, self.product)

        if self.target_res != res or (self.resolution_method != "Sampling" and res != 20):
            self.resample_bands(corrected_product)

        return self.extract_corrected_band(corrected_product)

    def resample_bands(self, corrected_product):
        from esa_snappy import HashMap, GPF
        resample_params = HashMap()
        resample_params.put('sourceBandNames', self.band)
        resample_params.put('targetResolution', self.target_res)
        resample_params.put('upsampling', 'Nearest')
        resample_params.put('downsampling', 'Mean')
        return GPF.createProduct("Resample", resample_params, corrected_product)

    def extract_corrected_band(self, corrected_product):
        corrected_band_name = f"rBRR_{self.band}"
        if corrected_band_name not in corrected_product.getBandNames():
            raise RuntimeError(f"Error: The corrected band '{corrected_band_name}' is not available after correction.")

        band = corrected_product.getBand(corrected_band_name)
        width, height = band.getRasterWidth(), band.getRasterHeight()
        band_data = np.empty((height, width), dtype=np.float32)
        band.readPixels(0, 0, width, height, band_data)

        return band_data