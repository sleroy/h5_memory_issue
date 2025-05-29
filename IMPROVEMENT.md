# Memory Usage Improvements for Data Processing

This document outlines the memory optimization improvements implemented in `process_data_optimized.py` and `process_data_numpy.py` compared to the original `process_data.py` script.

## Problem Analysis

The original code exhibited several memory-related issues:

1. **Memory Not Decreasing**: Memory usage would spike and remain high, not returning to baseline levels after processing.
2. **Large Memory Fluctuations**: Memory usage showed significant oscillations during processing.
3. **High Peak Memory Usage**: The code required excessive memory, especially with large datasets.

## Root Causes Identified

After analyzing the memory usage patterns and code structure, we identified these key issues:

1. **Inefficient Data Conversion**: Converting NumPy arrays to Python lists with `.tolist()` creates duplicate data in memory.
2. **Missing Garbage Collection**: No explicit garbage collection after freeing large data structures.
3. **Memory Fragmentation**: Repeatedly creating and destroying large dictionaries causes memory fragmentation.
4. **All-at-once Dictionary Creation**: Creating the entire dictionary in one comprehension statement causes memory spikes.
5. **No Cleanup Between Files**: While there's cleanup between batches, there's no explicit cleanup between files.

## Implemented Improvements

### Version 1: Optimized Dictionary Approach (`process_data_optimized.py`)

This version maintains the dictionary-based approach but with significant optimizations:

- **Modular Code Structure**: Extracted batch processing into a separate function for better resource management.
- **Chunked Column Processing**: Process columns in smaller chunks (50 at a time) to reduce peak memory usage.
- **Explicit Garbage Collection**: Added `gc.collect()` calls after each processing stage.
- **Proper Resource Cleanup**: Using context managers to ensure file handles are properly closed.
- **Thread-Local Storage**: Added thread-local storage to prevent memory leaks in multi-threaded scenarios.

### Version 2: NumPy-Based Approach (`process_data_numpy.py`)

This version replaces Python dictionaries with NumPy structured arrays for maximum memory efficiency:

- **Structured NumPy Arrays**: Uses NumPy structured arrays instead of Python dictionaries.
- **Zero-Copy Operations**: Minimizes data duplication by working directly with NumPy arrays.
- **Reduced Type Conversion**: Avoids unnecessary conversions between NumPy arrays and Python lists.
- **Chunked Processing**: Still processes data in chunks to maintain low memory footprint.
- **Minimal Data Extraction**: Only extracts the minimal amount of data needed for results.

## Memory Management Improvements (Both Versions)

- **Explicit Garbage Collection**: Added `gc.collect()` calls after:
  - Each chunk of columns
  - Each batch processing
  - Each file processing
- **Proper Resource Cleanup**: Using context managers to ensure file handles are properly closed.
- **Reduced Intermediate Variables**: Minimize temporary variables that hold large data structures.

## Data Structure Optimizations

### Dictionary Version
- **Minimized Data Duplication**: Only convert NumPy arrays to lists when absolutely necessary.
- **Immediate Cleanup**: Clear and delete dictionaries as soon as they're no longer needed.

### NumPy Version
- **Structured Arrays**: Uses NumPy's memory-efficient structured arrays.
- **In-Place Operations**: Performs operations directly on NumPy arrays without creating copies.
- **Memory-Efficient Data Types**: Uses appropriate data types to minimize memory usage.
- **Vectorized Operations**: Takes advantage of NumPy's vectorized operations for efficiency.

## Performance Impact

The optimized versions should show:

1. **Lower Peak Memory Usage**: By processing columns in chunks and managing resources better.
2. **More Consistent Memory Release**: Through explicit garbage collection and better cleanup.
3. **Reduced Memory Fragmentation**: By minimizing the creation and destruction of large objects.
4. **Same Functional Results**: The output JSON structure remains identical to the original.

The NumPy version should show the most significant memory improvements due to:
- NumPy's more efficient memory layout
- Reduced overhead compared to Python dictionaries
- Avoiding unnecessary type conversions

## Verification

To verify the improvements:

1. Run all versions with the memory monitoring tool:
   ```bash
   ./monitor_python_memory.sh process_data.py
   ./monitor_python_memory.sh process_data_optimized.py
   ./monitor_python_memory.sh process_data_numpy.py
   ```

2. Compare the memory usage patterns in the generated PNG files.

3. Compare the output results:
   ```bash
   diff -y <(jq -S . processing_results.json) <(jq -S . processing_results_optimized.json)
   diff -y <(jq -S . processing_results.json) <(jq -S . processing_results_numpy.json)
   ```

## Additional Recommendations

For further improvements:

1. **Memory-Mapped Files**: Consider using memory-mapped files for very large datasets.
2. **Streaming Processing**: Implement true streaming processing for extremely large files.
3. **Profiling Tools**: Use specialized memory profiling tools like `memory_profiler` or `tracemalloc`.
4. **Batch Size Tuning**: Experiment with different batch sizes to find the optimal balance.
5. **Data Compression**: Use compressed data formats or compression within HDF5 files.
6. **Native Extensions**: For extreme performance, consider rewriting critical sections in Cython or C extensions.

## Conclusion

The memory issues in the original code stemmed primarily from Python's memory management behavior combined with inefficient data handling patterns. Both optimized versions address these issues while maintaining the same functionality, with the NumPy-based approach likely providing the most significant memory efficiency improvements due to its more compact data representation and reduced type conversions.
