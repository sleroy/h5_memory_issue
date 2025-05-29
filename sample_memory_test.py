#!/usr/bin/env python3
"""
A simple Python script that gradually increases memory usage for testing.
"""
import time
import sys

# List to store data and increase memory usage
data = []

print("Starting memory test...")
print("Press Ctrl+C to stop")

try:
    # Gradually increase memory usage
    for i in range(10):
        # Allocate approximately 10MB of memory each iteration
        chunk = [0] * (10 * 1024 * 1024 // 8)  # Each number is 8 bytes
        data.append(chunk)
        print(f"Allocated chunk {i+1}/10 (approx. {(i+1)*10}MB)")
        time.sleep(2)  # Wait for 2 seconds between allocations
    
    print("Memory allocation complete. Holding for 5 seconds...")
    time.sleep(5)
    
except KeyboardInterrupt:
    print("\nTest interrupted by user")

print("Test complete")
