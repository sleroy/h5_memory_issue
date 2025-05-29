# Ferrari Memory Profiler

A tool for monitoring, analyzing, and optimizing Python process memory usage in real-time.

## Features

- Real-time memory usage monitoring of Python processes
- Incremental visualization with gnuplot
- Tracks both RSS (Resident Set Size) and VSZ (Virtual Memory Size)
- Customizable sampling interval
- Outputs both raw CSV data and PNG visualizations
- Timestamped debug files for historical comparison
- Memory optimization examples and strategies

## Memory Monitoring Tool

```bash
./monitor_python_memory.sh <python_script.py> [sampling_interval_seconds] [output_directory]
```

### Parameters

- `python_script.py`: The Python script to monitor
- `sampling_interval_seconds`: Optional. How frequently to sample memory usage (default: 1 second)
- `output_directory`: Optional. Where to save output files (default: current directory)

### Output Files

- `<script_name>_memory_usage.csv`: Raw memory usage data
- `<script_name>_memory_usage.png`: Memory usage visualization
- `YYYYMMDD_HHMMSS_<script_name>_memory_debug.csv`: Timestamped debug data
- `YYYYMMDD_HHMMSS_<script_name>_memory_debug.png`: Timestamped debug visualization

## Example Scripts

This repository includes several Python scripts that demonstrate memory usage patterns and optimization techniques:

1. **produce_data.py**: Generates test HDF5 files for memory profiling
2. **process_data.py**: Original data processing script with memory inefficiencies
3. **process_data_optimized.py**: Optimized version using dictionary-based approach
4. **process_data_numpy.py**: Highly optimized version using NumPy structured arrays

## Memory Optimization Strategies

The repository demonstrates several memory optimization techniques:

- Chunked data processing
- Explicit garbage collection
- NumPy structured arrays
- Resource cleanup with context managers
- Minimizing data duplication
- Reducing type conversions

For detailed information on all improvements, see the `IMPROVEMENT.md` file.

## Usage Examples

### Generate Test Data

```bash
python produce_data.py
```

### Monitor Original Script

```bash
./monitor_python_memory.sh process_data.py 2
```

### Compare Optimized Versions

```bash
./monitor_python_memory.sh process_data_optimized.py 2
./monitor_python_memory.sh process_data_numpy.py 2
```

## Requirements

- Bash
- Python
- gnuplot
- NumPy
- h5py

## Analysis Results

For a detailed analysis of memory usage patterns and optimization results, see the `AmazonQ.md` file.
