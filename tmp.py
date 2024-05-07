import os

def list_files_in_directory(directory):
    # Get a list of all files and directories in the specified directory
    files = os.listdir(directory)
    # Return only the files (not directories)
    return [file for file in files if os.path.isfile(os.path.join(directory, file))]

# Example usage:
directory_path = "arxiv"
files_list = list_files_in_directory(directory_path)
print(files_list)