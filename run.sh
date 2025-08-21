#!bin/bash

# Destination Analysis - Run
INPUT_DIR="Path to input directory"
OUTPUT_BASE="Path to ouput file"

# ## First step: extract domain-ip mappings and get domain list from DNS/TLS data
for INPUT_FILE in "${INPUT_DIR}"*; do
    echo "Running $INPUT_FILE"
    FILENAME=$(basename $INPUT_FILE)
    # exp name 2019idle for input_2019idle.txt
    EXP=${FILENAME:6:-4}
    OUTPUT_DIR="${OUTPUT_BASE}${EXP}"
    if [ -d "$OUTPUT_DIR/domain_list" ]; then
        echo "Already done $INPUT_FILE"
        continue
    else
        mkdir $OUTPUT_DIR
    fi
    python3 destination_analysis.py domains --input_file $INPUT_FILE --output_dir $OUTPUT_DIR --exp $EXP
    echo "Done $INPUT_FILE"
    # exit 1
done

## Second step: extract destination IPs and get destination list from domain-ip mappings
for INPUT_FILE in "${INPUT_DIR}"*; do
    echo "Running $INPUT_FILE"
    FILENAME=$(basename $INPUT_FILE)
    EXP=${FILENAME:6:-4}
    OUTPUT_DIR="${OUTPUT_BASE}${EXP}"
    if [ -d "$OUTPUT_DIR/ip_list" ]; then
        # echo "Already done $INPUT_FILE"
        # continue
        echo "$INPUT_FILE"
    else
        mkdir $OUTPUT_DIR
    fi
    python3 destination_analysis.py map_ips --input_file $INPUT_FILE --output_dir $OUTPUT_DIR --exp $EXP
    echo "Done $INPUT_FILE"
    # exit 1
done
