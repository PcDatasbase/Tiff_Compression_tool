import tifffile
import os
from pathlib import Path
from compression_check import check_compression


def is_already_compressed(file_path):
    """
    Check if a TIFF file is already compressed.
    Returns tuple: (is_compressed: bool, compression_method: str)
    """
    try:
        with tifffile.TiffFile(file_path) as tif:
            # Get the first page's compression
            compression = tif.pages[0].compression
            
            # Compression types:
            # 1 = No compression
            # 5 = LZW
            # 8 = ZIP/Deflate
            # 32773 = PackBits
            # etc.
            
            compression_map = {
                1: 'none',
                5: 'lzw',
                8: 'zip/deflate',
                32773: 'packbits',
                32946: 'deflate'
            }
            
            compression_name = compression_map.get(compression, f'unknown ({compression})')
            is_compressed = compression != 1  # 1 means uncompressed
            
            return is_compressed, compression_name
    except Exception as e:
        raise Exception(f"Error checking compression status: {str(e)}")


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
            raise Exception(f"Tiff file compression failed: {str(e)}")

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
                output_path = output_dir / f"_{tiff_file.name}"

                stats = compressor.compress_with_tifffile(output_path, method)

                stats['filename'] = tiff_file.name
                results.append(stats)
            except Exception as e:
                print(f"Error processing {tiff_file}: {str(e)}")
        return results

    @classmethod
    def compress_file(cls, file, compression_type='zip', skip_if_compressed=True):
        """
        Compress a TIFF file.
        
        Args:
            file: Path to the TIFF file
            compression_type: Compression method to use ('zip', 'lzw', 'packbits')
            skip_if_compressed: If True, skip compression for already-compressed files
            
        Returns:
            tuple: (output_path, was_already_compressed, existing_compression_method)
        """
        # Check if already compressed
        is_compressed, existing_method = is_already_compressed(file)
        
        if skip_if_compressed and is_compressed:
            return file, True, existing_method
        
        folder = os.path.abspath(os.path.join(file, os.pardir))
        name = os.path.join(folder, os.path.splitext(os.path.basename(file))[0])
        compressed_name = name + '_' + compression_type + ".tif"

        # For a single file
        compressor = TiffCompressor(file)
        compressor.compress_with_tifffile(compressed_name, method=compression_type)
        return compressed_name, False, None

    @classmethod
    def compress_and_check(cls, file):
        compressed_filename = cls.compress_file(file)
        check_compression(file, compressed_filename)




