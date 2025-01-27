class WiPE:
    """Implements the WiPE algorithm for processing satellite image bands."""

    def __init__(self, bands):
        """Initializes the WiPE class with the provided bands."""
        self.bands = bands
        self.mask = None

    def apply(self):
        """Applies WiPE calculations and generates a mask based on the input bands."""
        self._verify_band_dimensions()
        self.mask = np.ones_like(self.bands[2], dtype=np.uint16)
        self._apply_conditions()
        self._normalize_bands()
        return self.mask

    def _verify_band_dimensions(self):
        """Verifies that all bands have the same dimensions."""
        for i in range(len(self.bands) - 1):
            if self.bands[i].shape != self.bands[i + 1].shape:
                raise ValueError("All bands must have the same dimensions.")

    def _apply_conditions(self):
        """Applies initial filtering conditions to the mask."""
        self.mask[np.isnan(self.bands[0]) | np.isnan(self.bands[1]) | 
                  np.isnan(self.bands[2]) | np.isnan(self.bands[3]) | 
                  (self.bands[3] == 0)] = 0

        self.mask[(self.bands[5] / self.bands[2] > 0.69) & (self.mask == 1)] = 10
        self.mask[(self.bands[5] > 0.035) & (self.mask == 1)] = 20
        self.mask[(self.bands[0] < 0.0065) | (self.bands[4] > 0.01072) & (self.mask == 1)] = 30

    def _normalize_bands(self):
        """Normalizes the bands and applies additional conditions."""
        max_bands = [band / np.nanmax(band) for band in self.bands[:3]]
        stacked = np.stack(max_bands, axis=0)
        source_max = np.argmax(stacked, axis=0)
        source_min = np.argmin(stacked, axis=0)

        rows, cols = self.bands[4].shape
        for i in range(rows):
            for j in range(cols):
                if self.mask[i, j] == 1:
                    self._apply_additional_conditions(i, j, stacked, source_max, source_min)

    def _apply_additional_conditions(self, i, j, stacked, source_max, source_min):
        """Applies additional conditions based on the source of maximum values."""
        if source_max[i, j] == 0:
            if stacked[0, i, j] > (-2.93 * (self.bands[5][i, j] / self.bands[3][i, j]) + 2):
                self.mask[i, j] = 40
            if (self.bands[6][i, j] / self.bands[2][i, j] > 0.28 or
                (stacked[0, i, j] - stacked[source_min[i, j], i, j]) / stacked[0, i, j] < 0.12):
                self.mask[i, j] = 50
        elif source_max[i, j] == 1:
            if ((stacked[1, i, j] - stacked[source_min[i, j], i, j]) / stacked[1, i, j] < 0.04 or
                self.bands[6][i, j] / self.bands[2][i, j] > 0.46):
                self.mask[i, j] = 60
            if self.bands[2][i, j] < self.bands[0][i, j] and stacked[1, i, j] > 0.3:
                if ((stacked[1, i, j] - stacked[source_min[i, j], i, j]) / stacked[1, i, j] < 0.12):
                    self.mask[i, j] = 70
        elif source_max[i, j] == 2:
            if ((self.bands[2][i, j] - self.bands[1][i, j] > 0.001) or
                (stacked[2, i, j] - stacked[source_min[i, j], i, j]) / stacked[2, i, j] < 0.05):
                self.mask[i, j] = 80
            if stacked[2, i, j] > (-1.107 * (self.bands[5][i, j] / self.bands[0][i, j]) + 0.748):
                self.mask[i, j] = 90
        else:
            raise ValueError("Error in index processing.")