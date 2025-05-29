#!/bin/bash

# Check if process ID is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <python_script.py> [sampling_interval_seconds]"
    exit 1
fi

# Check if gnuplot is installed
if ! command -v gnuplot &> /dev/null; then
    echo "Error: gnuplot is not installed. Please install it with:"
    echo "sudo apt-get install -y gnuplot  # For Debian/Ubuntu"
    echo "sudo yum install -y gnuplot      # For CentOS/RHEL"
    exit 1
fi

PYTHON_SCRIPT=$1
INTERVAL=${2:-1}  # Default to 1 second if not specified
OUTPUT_DIR=${3:-.}  # Default to current directory
OUTPUT_PREFIX=$(basename "$PYTHON_SCRIPT" .py)
CSV_FILE="${OUTPUT_DIR}/${OUTPUT_PREFIX}_memory_usage.csv"
PNG_FILE="${OUTPUT_DIR}/${OUTPUT_PREFIX}_memory_usage.png"
GNUPLOT_SCRIPT="${OUTPUT_DIR}/${OUTPUT_PREFIX}_plot.gnu"

# Create gnuplot script template
cat > "$GNUPLOT_SCRIPT" << EOL
set terminal png size 1200,800
set output '$PNG_FILE'
set title 'Memory Usage: $PYTHON_SCRIPT (PID: \$PID)\nDate: \$CURRENT_DATE'
set xlabel 'Time (seconds)'
set ylabel 'Memory (KB)'
set grid
set key outside right top
set datafile separator ','

# Get the start time to calculate relative time
start_time = system("head -2 $CSV_FILE | tail -1 | cut -d',' -f1")

plot '$CSV_FILE' using (\$1-start_time):2 with lines lw 2 title 'RSS (Resident Set Size)', \
     '$CSV_FILE' using (\$1-start_time):3 with lines lw 2 title 'VSZ (Virtual Memory Size)'
EOL

# Start the Python process
python $PYTHON_SCRIPT &
PID=$!

echo "Monitoring Python process with PID: $PID"
echo "Time,RSS_KB,VSZ_KB" > "$CSV_FILE"

# Function to update the plot
update_plot() {
    CURRENT_DATE=$(date "+%Y-%m-%d %H:%M:%S")
    # Only generate plot if we have at least 2 data points
    if [ $(wc -l < "$CSV_FILE") -gt 2 ]; then
        gnuplot -e "PID='$PID'; CURRENT_DATE='$CURRENT_DATE'" "$GNUPLOT_SCRIPT" 2>/dev/null
    fi
}

# Monitor until the process ends
echo "Generating incremental plots. Press Ctrl+C to stop monitoring."
while kill -0 $PID 2>/dev/null; do
    # Get memory usage (RSS and VSZ in KB)
    MEM_INFO=$(ps -p $PID -o rss=,vsz=)
    if [ $? -ne 0 ]; then
        break  # Process has ended
    fi
    
    RSS=$(echo $MEM_INFO | awk '{print $1}')
    VSZ=$(echo $MEM_INFO | awk '{print $2}')
    TIMESTAMP=$(date +%s)
    
    echo "$TIMESTAMP,$RSS,$VSZ" >> "$CSV_FILE"
    
    # Update the plot every interval
    update_plot
    
    sleep $INTERVAL
done

echo "Process completed. Memory usage data saved to $CSV_FILE"

# Generate final plot
echo "Generating final memory usage plot..."
CURRENT_DATE=$(date "+%Y-%m-%d %H:%M:%S")
gnuplot -e "PID='$PID'; CURRENT_DATE='$CURRENT_DATE'" "$GNUPLOT_SCRIPT"

if [ $? -eq 0 ]; then
    echo "Final plot generated: $PNG_FILE"
    # Clean up the gnuplot script
    rm -f "$GNUPLOT_SCRIPT"
else
    echo "Error generating final plot"
fi
