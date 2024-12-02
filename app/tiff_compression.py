import tifffile
import os
from pathlib import Path
from compression_check import check_compression


class TiffCompressor:
    """
    Handles lossless compression of TIFF files using various methods.
    Supports single images and image sequences.
    """

    COMPRESSION_METHODS = {
        'lzw': {'pillow_method': 'tiff_lzw', 'tifffile_method': 'lzw'},
        'zip': {'pillow_method': 'tiff_deflate', 'tifffile_method': 'zlib'},
        'packbits': {'pillow_method': 'tiff_adobe_deflate', 'tifffile_method': 'packbits'}
    }

    def __init__(self, input_path):
        self.input_path = Path(input_path)
        self.original_size = os.path.getsize(input_path)

    def compress_with_tifffile(self, output_path, method='lzw'):
        """
        Compress using tifffile library.
        Better for multi-frame TIFF sequences.
        """
        try:
            with tifffile.TiffFile(self.input_path) as tif:
                data = tif.asarray()
                metadata = tif.imagej_metadata

            tifffile.imwrite(output_path,
                             data,
                             compression=self.COMPRESSION_METHODS[method]['tifffile_method'],
                             metadata=metadata,
                             imagej=True if metadata else False)
            return self._get_compression_stats(output_path)
        except Exception as e:
            raise Exception(f"Tifffile compression failed: {str(e)}")

    def _get_compression_stats(self, output_path):
        """Calculate compression statistics."""
        compressed_size = os.path.getsize(output_path)
        ratio = (1 - compressed_size / self.original_size) * 100
        return {
            'original_size_mb': self.original_size / (1024 * 1024),
            'compressed_size_mb': compressed_size / (1024 * 1024),
            'compression_ratio': ratio,
            'space_saved_mb': (self.original_size - compressed_size) / (1024 * 1024)
        }


class TiffCompressorManager:
    def __init__(self, path):
        self.path = path

    @classmethod
    def batch_compress_directory(cls, input_dir, output_dir, method='lzw'):
        """
        Batch compress all TIFF files in a directory.
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        results = []
        for tiff_file in input_dir.glob('*.tif*'):
            try:
                compressor = TiffCompressor(tiff_file)
                output_path = output_dir / f"compressed_{tiff_file.name}"

                stats = compressor.compress_with_tifffile(output_path, method)

                stats['filename'] = tiff_file.name
                results.append(stats)
            except Exception as e:
                print(f"Error processing {tiff_file}: {str(e)}")
        return results

    @classmethod
    def compress_file(cls, file, compression_type='zip'):
        folder = os.path.abspath(os.path.join(file, os.pardir))
        name = os.path.join(folder, os.path.splitext(os.path.basename(file))[0])
        compressed_name = name + '_compressed_' + compression_type + ".tif"

        # For a single file
        compressor = TiffCompressor(file)
        compressed_file = compressor.compress_with_tifffile(compressed_name, method=compression_type)
        return compressed_name

        # For a directory of files
        # results = batch_compress_directory(
        #     input_dir="raw_images/",
        #     output_dir="compressed_images/",
        #     method='lzw',
        #     use_tifffile=True
        # )

    @classmethod
    def compress_and_check(cls, file):
        compressed_filename = cls.compress_file(file)
        check_compression(file, compressed_filename)


# This is a test
if __name__ == '__main__':
    folder = "C:\\Git\\tests\\bak_09_12_24\\test_for_ai\\Dossier_A\\"
    TiffCompressorManager.compress_and_check(folder + "1.tif")

