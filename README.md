# Ferrari Memory Profiler

A tool for monitoring and visualizing Python process memory usage in real-time.

## Features

- Real-time memory usage monitoring of Python processes
- Incremental visualization with gnuplot
- Tracks both RSS (Resident Set Size) and VSZ (Virtual Memory Size)
- Customizable sampling interval
- Outputs both raw CSV data and PNG visualizations

## Usage

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

## Requirements

- Bash
- Python
- gnuplot

## Example

```bash
./monitor_python_memory.sh process_data.py 2
```

This will monitor the memory usage of `process_data.py` with a 2-second sampling interval.
