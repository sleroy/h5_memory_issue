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
    Process the test files using similar pattern to the original code
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
            
            with open(file_path, 'rb') as s3file:
                with h5py.File(file_path, 'r') as f:
                    DATA_DICT = {
                        str(c[0]): f[f"GROUP{c[1]}"][int(c[2])-1][bounds[0]:bounds[1]].tolist()
                        for c in columns_group_position
                    }
            
            end_time = time.time()
            log_memory("After dictionary creation")
            
            # Save some results for validation
            batch_result = {
                'file': filename,
                'batch': n,
                'bounds': bounds,
                'processing_time': end_time - start_time,
                'dict_keys': list(DATA_DICT.keys()),
                'first_values': {k: v[0] if len(v) > 0 else None 
                               for k, v in list(DATA_DICT.items())[:3]}  # Save first 3 keys only
            }
            results.append(batch_result)
            
            # Clean up
            DATA_DICT.clear()
            del DATA_DICT
    
    # Save results
    with open('processing_results.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    process_files()
