"""
TIFF Compression Tool
=====================

A Python package for lossless compression of TIFF images and sequences.

Main Components:
----------------
- TiffCompressor: Compress individual TIFF files
- TiffCompressorManager: Batch compress directories
- TiffVerifier: Verify compression integrity
- is_already_compressed: Check if a file is already compressed
- check_compression: Verify compression quality

Example Usage:
--------------
    from app import TiffCompressor, TiffVerifier

    # Compress a single file
    compressor = TiffCompressor('input.tif')
    stats = compressor.compress_with_tifffile('output.tif', method='lzw')
    
    # Verify compression
    verifier = TiffVerifier('input.tif', 'output.tif')
    results = verifier.verify_all()
    
    # Batch compress a directory
    from app import TiffCompressorManager
    TiffCompressorManager.batch_compress_directory('input_dir', 'output_dir', method='lzw')
"""

__version__ = '1.0.0'
__author__ = 'GRESSE Mickael'

from .tiff_compression import (
    TiffCompressor,
    TiffCompressorManager,
    is_already_compressed
)

from .compression_check import (
    TiffVerifier,
    check_compression
)

__all__ = [
    'TiffCompressor',
    'TiffCompressorManager',
    'TiffVerifier',
    'is_already_compressed',
    'check_compression',
    '__version__',
]
