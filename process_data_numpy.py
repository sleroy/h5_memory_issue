import h5py
import numpy as np
import os
import time
import psutil
import json
import gc
from datetime import datetime

def log_memory(message):
    """Simple memory logger"""
    process = psutil.Process()
    memory_info = process.memory_info().rss / 1024 / 1024  # MB
    print(f"{message}: {memory_info:.2f} MB")

def process_files(batch_size=100000):
    """
    Process the test files using NumPy arrays instead of Python dictionaries
    """
    # Load column information
    columns_group_position = np.load('test_data/columns_info.npy')
    
    # Get list of test files
    files = [f for f in os.listdir('test_data') if f.endswith('.h5')]
    
    results = []
    
    for file_idx, filename in enumerate(files):
        file_path = os.path.join('test_data', filename)
        print(f"\nProcessing file: {filename}")
        
        # Calculate batches
        with h5py.File(file_path, 'r') as f:
            total_rows = f['GROUP1'].shape[1]
            
        tables_batches = [(i, min(i + batch_size, total_rows)) 
                         for i in range(0, total_rows, batch_size)]
        
        for n, bounds in enumerate(tables_batches):
            print(f"Processing batch {n+1}/{len(tables_batches)}")
            log_memory("Before file open")
            
            start_time = time.time()
            
            # Create a structured NumPy array instead of a dictionary
            # First, determine the column names and data types
            column_names = [str(c[0]) for c in columns_group_position]
            
            # Process in chunks to reduce peak memory
            chunk_size = 50  # Process 50 columns at a time
            all_data = None
            
            with h5py.File(file_path, 'r') as f:
                # Get the number of rows in this batch
                batch_rows = bounds[1] - bounds[0]
                
                # Create a structured array once we know the shape
                dtype_list = [(name, 'f8') for name in column_names]
                all_data = np.zeros(batch_rows, dtype=dtype_list)
                
                # Process columns in chunks
                for i in range(0, len(columns_group_position), chunk_size):
                    chunk = columns_group_position[i:i+chunk_size]
                    
                    for c in chunk:
                        col_name = str(c[0])
                        group_idx = int(c[1])
                        col_idx = int(c[2])-1
                        
                        # Get data directly into the structured array
                        all_data[col_name] = f[f"GROUP{group_idx}"][col_idx][bounds[0]:bounds[1]]
                    
                    # Force garbage collection after each chunk
                    gc.collect()
            
            end_time = time.time()
            log_memory("After array creation")
            
            # For compatibility with the original code, extract some sample data
            # but keep it minimal to avoid memory issues
            sample_data = {}
            for col_name in column_names[:10]:  # Only get first 10 columns for the sample
                sample_data[col_name] = all_data[col_name][:1].tolist()  # Just get first value
            
            # Save some results for validation
            batch_result = {
                'file': filename,
                'batch': n,
                'bounds': bounds,
                'processing_time': end_time - start_time,
                'dict_keys': column_names,
                'first_values': {k: sample_data[k][0] if len(sample_data[k]) > 0 else None 
                               for k in list(sample_data.keys())[:3]}  # Save first 3 keys only
            }
            results.append(batch_result)
            
            # Clean up
            del all_data
            del sample_data
            gc.collect()
            log_memory("After cleanup")
    
    # Save results
    with open('processing_results_numpy.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    log_memory("Process complete")

if __name__ == "__main__":
    process_files()
