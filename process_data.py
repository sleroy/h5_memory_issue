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

def process_files(batch_size=20000):  # Increased from 200 to 2000
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
                    # Create a larger dictionary by duplicating data multiple times
                    # This will increase memory usage significantly
                    base_data = {
                        str(c[0]): f[f"GROUP{c[1]}"][int(c[2])-1][bounds[0]:bounds[1]].tolist()
                        for c in columns_group_position
                    }
                    
                    # Duplicate the data to increase memory usage (5x more memory)
                    DATA_DICT = {}
                    for k, v in base_data.items():
                        DATA_DICT[k] = v
                        # Create additional copies with slightly modified keys
                        for i in range(1, 6):
                            DATA_DICT[f"{k}_copy_{i}"] = v.copy()
            
            end_time = time.time()
            log_memory("After dictionary creation")
            
            # Save some results for validation
            batch_result = {
                'file': filename,
                'batch': n,
                'bounds': bounds,
                'processing_time': end_time - start_time,
                'dict_keys': list(DATA_DICT.keys())[:10],  # Only save first 10 keys to avoid huge JSON
                'first_values': {k: v[0] if len(v) > 0 else None 
                               for k, v in list(DATA_DICT.items())[:3]}  # Save first 3 keys only
            }
            results.append(batch_result)
            
            # Clean up
            DATA_DICT.clear()
            del DATA_DICT
            
            # Force garbage collection after each batch
            gc.collect()
            log_memory("After garbage collection")
    
    # Save results
    with open('processing_results.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    process_files()
