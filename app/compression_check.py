import numpy as np
import tifffile
import hashlib
from pathlib import Path
from typing import Tuple, Dict, Union
import matplotlib.pyplot as plt
import os


class TiffVerifier:
    """
    Verifies the integrity of compressed TIFF files against their originals
    using multiple verification methods.
    """

    def __init__(self, original_path: str, compressed_path: str):
        self.original_path = Path(original_path)
        self.compressed_path = Path(compressed_path)

    def verify_all(self) -> Dict[str, bool]:
        """Run all verification methods and return results."""
        results = {
            'pixel_values_match': self.verify_pixel_values(),
            'file_hash_different': self.verify_file_hashes(),  # Should be different
            'dimensions_match': self.verify_dimensions(),
            'metadata_matches': self.verify_metadata(),
            'statistical_match': self.verify_statistics()
        }
        return results

    def verify_pixel_values(self) -> bool:
        """
        Compare pixel values between original and compressed images.
        Returns True if all pixels match exactly.
        """
        try:
            # Using tifffile for better handling of multi-frame TIFFs
            original = tifffile.imread(self.original_path)
            compressed = tifffile.imread(self.compressed_path)

            if original.shape != compressed.shape:
                return False

            return np.array_equal(original, compressed)
        except Exception as e:
            raise Exception(f"Pixel comparison failed: {str(e)}")

    def verify_file_hashes(self) -> bool:
        """
        Compare file hashes. For compressed files, these should be different
        even though the pixel data is the same.
        """

        def get_file_hash(file_path: Path) -> str:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()

        original_hash = get_file_hash(self.original_path)
        compressed_hash = get_file_hash(self.compressed_path)
        return original_hash != compressed_hash

    def verify_dimensions(self) -> bool:
        """Verify that image dimensions match."""
        with tifffile.TiffFile(self.original_path) as orig:
            orig_shape = orig.series[0].shape

        with tifffile.TiffFile(self.compressed_path) as comp:
            comp_shape = comp.series[0].shape

        return orig_shape == comp_shape

    def verify_metadata(self) -> bool:
        """Verify crucial metadata matches."""
        with tifffile.TiffFile(self.original_path) as orig:
            orig_meta = orig.imagej_metadata

        with tifffile.TiffFile(self.compressed_path) as comp:
            comp_meta = comp.imagej_metadata

        # If neither has metadata, consider it a match
        if orig_meta is None and comp_meta is None:
            return True

        # If one has metadata and the other doesn't, it's a mismatch
        if (orig_meta is None) != (comp_meta is None):
            return False

        # Compare relevant metadata fields
        crucial_fields = ['frames', 'slices', 'channels']
        return all(orig_meta.get(field) == comp_meta.get(field)
                   for field in crucial_fields
                   if field in orig_meta)

    def verify_statistics(self) -> bool:
        """
        Verify statistical properties match (min, max, mean, std).
        """
        original = tifffile.imread(self.original_path)
        compressed = tifffile.imread(self.compressed_path)

        stats_match = {
            'min': np.min(original) == np.min(compressed),
            'max': np.max(original) == np.max(compressed),
            'mean': np.mean(original) == np.mean(compressed),
            'std': np.std(original) == np.std(compressed)
        }

        return all(stats_match.values())

    def generate_difference_map(self, frame: int = 0) -> np.ndarray:
        """
        Generate a difference map between original and compressed images.
        Returns the difference array (should be all zeros for lossless compression).
        """
        original = tifffile.imread(self.original_path)
        compressed = tifffile.imread(self.compressed_path)

        if len(original.shape) > 2:
            original = original[frame]
            compressed = compressed[frame]

        return original.astype(float) - compressed.astype(float)

    def plot_verification(self, frame: int = 0) -> None:
        """
        Create a visual verification plot comparing original and compressed images.
        """
        diff_map = self.generate_difference_map(frame)

        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))

        # Original image
        original = tifffile.imread(self.original_path)
        if len(original.shape) > 2:
            original = original[frame]
        ax1.imshow(original, cmap='gray')
        ax1.set_title('Original')

        # Compressed image
        compressed = tifffile.imread(self.compressed_path)
        if len(compressed.shape) > 2:
            compressed = compressed[frame]
        ax2.imshow(compressed, cmap='gray')
        ax2.set_title('Compressed')

        # Difference map
        im = ax3.imshow(diff_map, cmap='RdBu')
        ax3.set_title('Difference Map')
        plt.colorbar(im, ax=ax3)

        plt.tight_layout()
        plt.show()


def check_compression(original, compressed, plot=False):
    success = None
    # After compression
    verifier = TiffVerifier(original, compressed)

    # Run complete verification
    results = verifier.verify_all()

    if all(results.values()):
        print(original, ": Compression successful with no data loss!")
        success = True
    else:
        print("Issues detected:")
        for test, passed in results.items():
            if not passed:
                print(f"- Failed: {test}")
        success = False

    # Generate visual verification
    if plot:
        verifier.plot_verification()
    return success


def check_both(file, plot=False):
    folder = os.path.abspath(os.path.join(file, os.pardir))
    name = os.path.join(folder, os.path.splitext(os.path.basename(file))[0])
    # check_compression(file, name + "_compressed_lzw.tif", plot)
    check_compression(file, name + "_compressed_zip.tif", plot)
