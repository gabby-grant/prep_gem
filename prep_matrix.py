#!/usr/bin/env python3  # Specifies the interpreter to use when executing this script

# Import necessary libraries for file operations, pattern matching, data manipulation, command-line parsing, and system functions
import os  # Provides functions for interacting with the operating system and file paths
import glob  # Used for Unix style pathname pattern expansion
import pandas as pd  # Data manipulation library for creating and working with DataFrames
import argparse  # Provides command-line argument parsing functionality
import sys  # Provides access to some variables used or maintained by the interpreter

def parse_args():  # Function to handle command-line arguments
    parser = argparse.ArgumentParser(description='Parse gene names and expression levels from gene expression files')  # Creates an argument parser with description
    parser.add_argument('-i', '--input', required=True,  # Adds required input directory argument
                        help='Input directory containing sample folders')
    parser.add_argument('-o', '--output_file', required=True, help='Output file name')  # Adds required output file argument
    parser.add_argument('-c', '--expression_column', default='stranded_second',  # Adds optional expression column argument with default value
                        help='Column name for expression values (default: stranded_second)')
    parser.add_argument('-e', '--extension', default='',  # Adds optional file extension filter argument
                        help='File extension to filter by (default: process all files)')
    return parser.parse_args()  # Parses arguments and returns them

def find_sample_folders(input_path):  # Function to identify sample folders in the input directory
    """Find all subdirectories in the input path that could be sample folders"""
    if not os.path.isdir(input_path):  # Checks if the input path is a valid directory
        print(f"Error: {input_path} is not a directory")  # Prints error message if not a directory
        sys.exit(1)  # Exits the program with error code 1
        
    # Get all subdirectories - creates a list of full paths to all subdirectories in the input path
    sample_folders = [os.path.join(input_path, d) for d in os.listdir(input_path) 
                     if os.path.isdir(os.path.join(input_path, d))]
    
    return sample_folders  # Returns the list of sample folder paths

def find_files_in_folder(folder_path, extension=''):  # Function to find files in a folder, optionally filtering by extension
    """Find all files in a folder, optionally filtering by extension"""
    files = []  # Initialize empty list to store file paths
    
    if extension:  # If an extension was specified
        pattern = os.path.join(folder_path, f"*.{extension}")  # Create pattern to match files with that extension
        files = glob.glob(pattern)  # Find all files matching the pattern
    else:  # If no extension was specified
        # Get all files in the directory (not subdirectories)
        files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
                 if os.path.isfile(os.path.join(folder_path, f))]
    
    return files  # Return the list of file paths

def process_file(file_path, expression_column, combined_data, sample_name=None):  # Function to process a single gene expression file
    """Process a single file and extract gene names and expression values"""
    if sample_name is None:  # If no sample name was provided
        # Use the parent directory name as the sample name
        sample_name = os.path.basename(os.path.dirname(file_path))  # Extract the directory name from the file path
    
    print(f"Processing file for sample {sample_name}: {os.path.basename(file_path)}")  # Print status message
    
    try:  # Try to process the file, with error handling
        # Read the file line by line to handle the special format
        with open(file_path, 'r') as f:  # Open the file for reading
            lines = f.readlines()  # Read all lines into a list
        
        # Find the header line (contains gene_name)
        header_index = -1  # Initialize header index to -1 (not found)
        for i, line in enumerate(lines):  # Loop through each line with its index
            if 'gene_name' in line:  # Check if this line contains the header
                header_index = i  # Store the index of the header line
                break  # Exit the loop once header is found
        
        if header_index == -1:  # If header wasn't found
            print(f"Warning: No header with 'gene_name' found in {file_path}. Skipping.")  # Print warning
            return  # Skip this file
        
        # Parse the header line to get column names
        headers = lines[header_index].strip().split('\t')  # Split the header line by tabs
        
        # Check if required columns exist
        if 'gene_name' not in headers:  # Check if gene_name column exists
            print(f"Warning: 'gene_name' column not found in {file_path}. Skipping.")  # Print warning
            return  # Skip this file
            
        if expression_column not in headers:  # Check if the specified expression column exists
            print(f"Warning: '{expression_column}' column not found in {file_path}. Available columns: {headers}")  # Print warning with available columns
            return  # Skip this file
        
        gene_name_index = headers.index('gene_name')  # Get the index of the gene_name column
        expression_index = headers.index(expression_column)  # Get the index of the expression column
        
        # Process data lines (skip metadata and header)
        for line in lines[header_index + 1:]:  # Loop through each line after the header
            parts = line.strip().split('\t')  # Split the line by tabs
            
            # Skip lines that don't have enough columns
            if len(parts) <= max(gene_name_index, expression_index):  # Check if line has enough columns
                continue  # Skip to next line
                
            # Skip summary lines (like N_unmapped, N_multimapping, etc.)
            if gene_name_index >= len(parts) or parts[gene_name_index] == '' or parts[gene_name_index].startswith('N_'):  # Check for summary lines
                continue  # Skip to next line
            
            gene_name = parts[gene_name_index]  # Get the gene name
            
            # Skip entries without a gene name
            if not gene_name or gene_name == '':  # Check if gene name is empty
                continue  # Skip to next line
                
            try:  # Try to convert expression value to float
                expression = float(parts[expression_index])  # Convert expression value to float
            except (ValueError, IndexError):  # Handle conversion errors
                # Skip if expression value is not a number
                continue  # Skip to next line
            
            # Store the data in the combined_data dictionary
            if gene_name not in combined_data:  # If this is the first time seeing this gene
                combined_data[gene_name] = {}  # Create a new dictionary for this gene
            
            combined_data[gene_name][sample_name] = expression  # Store the expression value for this gene and sample
            
    except Exception as e:  # Catch any other errors
        print(f"Error processing {file_path}: {e}")  # Print error message

def main():  # Main function that runs the program
    args = parse_args()  # Parse command-line arguments
    
    # Find all sample folders in the input directory
    sample_folders = find_sample_folders(args.input)  # Get list of sample folders
    
    if not sample_folders:  # If no sample folders were found
        print(f"No sample folders found in {args.input}")  # Print error message
        print(f"Directory contents of {args.input}:")  # Print directory contents for debugging
        try:  # Try to list directory contents
            contents = os.listdir(args.input)  # Get directory contents
            if contents:  # If directory is not empty
                for item in contents:  # Loop through each item
                    item_path = os.path.join(args.input, item)  # Get full path to item
                    if os.path.isdir(item_path):  # Check if item is a directory
                        print(f"  {item}/ (directory)")  # Print directory name
                    else:  # If item is a file
                        print(f"  {item} (file)")  # Print file name
            else:  # If directory is empty
                print("  (empty directory)")  # Print message
        except Exception as e:  # Handle errors
            print(f"  Error listing directory: {e}")  # Print error message
        sys.exit(1)  # Exit with error code
    
    print(f"Found {len(sample_folders)} sample folders:")  # Print number of sample folders found
    for folder in sample_folders:  # Loop through each sample folder
        print(f"  {folder}")  # Print folder path
    
    # Create a dictionary to store the combined data
    # Key: gene_name, Value: dictionary with sample_name -> expression_value
    combined_data = {}  # Initialize empty dictionary for combined data
    
    # Process each sample folder
    for folder in sample_folders:  # Loop through each sample folder
        sample_name = os.path.basename(folder)  # Get sample name from folder name
        print(f"Processing sample folder: {sample_name}")  # Print status message
        
        # Find files in the folder
        files = find_files_in_folder(folder, args.extension)  # Get list of files in folder
        
        if not files:  # If no files were found
            print(f"  No files found in {folder}")  # Print warning
            continue  # Skip to next folder
            
        print(f"  Found {len(files)} files")  # Print number of files found
        
        # Process each file in the folder
        for file_path in files:  # Loop through each file
            process_file(file_path, args.expression_column, combined_data, sample_name)  # Process the file
    
    # Convert the combined data to a DataFrame for easier manipulation and output
    print("Creating combined data frame...")  # Print status message
    result_df = pd.DataFrame.from_dict(combined_data, orient='index')  # Create DataFrame from combined data
    result_df.index.name = 'gene_name'  # Set index name to 'gene_name'
    
    # Save the combined data to the output file (keeping NA values)
    print(f"Saving results to {args.output_file}...")  # Print status message
    result_df.to_csv(args.output_file, sep='\t', na_rep='NA')  # Save DataFrame to TSV file
    
    print(f"Done! Processed data for {len(combined_data)} genes across {len(sample_folders)} samples.")  # Print completion message

if __name__ == "__main__":  # Check if script is being run directly (not imported)
    main()  # Run the main function