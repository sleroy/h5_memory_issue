import h5py
import numpy as np
import os
import time
import psutil
import json
import gc
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading

# Thread-local storage for data dictionaries to avoid memory leaks
thread_local = threading.local()

def log_memory(message):
    """Simple memory logger"""
    process = psutil.Process()
    memory_info = process.memory_info().rss / 1024 / 1024  # MB
    print(f"{message}: {memory_info:.2f} MB")

def process_batch(file_path, bounds, columns_group_position, batch_idx, filename):
    """Process a single batch with proper resource management"""
    start_time = time.time()
    
    # Use a context manager to ensure file handles are properly closed
    with h5py.File(file_path, 'r') as f:
        # Use numpy arrays directly instead of converting to lists
        # Only convert to list at the last moment if needed
        data_dict = {}
        
        # Process columns in smaller chunks to reduce peak memory
        chunk_size = 50  # Process 50 columns at a time
        for i in range(0, len(columns_group_position), chunk_size):
            chunk = columns_group_position[i:i+chunk_size]
            
            # Process this chunk of columns
            for c in chunk:
                col_name = str(c[0])
                group_idx = int(c[1])
                col_idx = int(c[2])-1
                
                # Get the data directly without intermediate variables
                data_dict[col_name] = f[f"GROUP{group_idx}"][col_idx][bounds[0]:bounds[1]].tolist()
            
            # Force garbage collection after each chunk to prevent memory buildup
            gc.collect()
    
    end_time = time.time()
    
    # Create batch result with minimal data
    batch_result = {
        'file': filename,
        'batch': batch_idx,
        'bounds': bounds,
        'processing_time': end_time - start_time,
        'dict_keys': list(data_dict.keys()),
        'first_values': {k: v[0] if len(v) > 0 else None 
                       for k, v in list(data_dict.items())[:3]}  # Save first 3 keys only
    }
    
    # Clean up
    data_dict.clear()
    del data_dict
    gc.collect()
    
    return batch_result

def process_files(batch_size=100000, max_workers=4):
    """
    Process the test files using similar pattern to the original code
    but with optimizations for memory usage
    """
    log_memory("Starting process")
    
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
        
        file_results = []
        
        # Process batches sequentially to avoid excessive memory usage
        for n, bounds in enumerate(tables_batches):
            print(f"Processing batch {n+1}/{len(tables_batches)}")
            log_memory("Before batch processing")
            
            batch_result = process_batch(file_path, bounds, columns_group_position, n, filename)
            file_results.append(batch_result)
            
            log_memory("After batch processing")
            
            # Explicit cleanup after each batch
            gc.collect()
        
        # Add file results to overall results
        results.extend(file_results)
        
        # Cleanup after each file
        file_results = []
        gc.collect()
        log_memory(f"After processing file {filename}")
    
    # Save results
    with open('processing_results_optimized.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    log_memory("Process complete")

if __name__ == "__main__":
    process_files()
