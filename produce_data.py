import h5py
import numpy as np
import os

def generate_test_files(num_files=3, num_groups=2, rows=1000000, cols=100):
    """
    Generate test HDF5 files with similar structure to your data
    """
    if not os.path.exists('test_data'):
        os.makedirs('test_data')
    
    # Generate some test column definitions
    columns_info = []
    for g in range(num_groups):
        for c in range(cols):
            columns_info.append((f'col_{g}_{c}', g+1, c+1))
    
    # Save columns info for the reader script
    np.save('test_data/columns_info.npy', columns_info)
    
    # Create test files
    for file_idx in range(num_files):
        filename = f'test_data/test_file_{file_idx}.h5'
        with h5py.File(filename, 'w') as f:
            for group_idx in range(num_groups):
                group_name = f'GROUP{group_idx+1}'
                # Create random data for each column in the group
                data = np.random.rand(cols, rows)  # Using random data
                f.create_dataset(group_name, data=data)
        
        print(f"Created file: {filename}")

    return columns_info

if __name__ == "__main__":
    generate_test_files()

    