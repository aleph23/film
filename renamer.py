import os
import sys

def rename_files(root_dir, pattern, new_name):
    count = 0
    matched_files = [filename for filename in os.listdir(root_dir) if pattern in filename]
    
    if len(matched_files) == 1:
        for filename in matched_files:
            old_path = os.path.join(root_dir, filename)
            new_path = os.path.join(root_dir, f"{new_name}{os.path.splitext(filename)[1]}")
            print(f'Renaming {old_path} to {new_path}')
            os.rename(old_path, new_path)
    else:
        for filename in matched_files:
            count += 1
            base, ext = os.path.splitext(filename)
            new_filename = f"{new_name}_{count:05d}{ext}"
            old_path = os.path.join(root_dir, filename)
            new_path = os.path.join(root_dir, new_filename)
            print(f'Renaming {old_path} to {new_path}')
            os.rename(old_path, new_path)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(f'Usage: {sys.argv[0]} ROOT_DIR=the beginning folder, PATTERN=what to search for, NEW_NAME=new_name_with_extension indicates that the NEW_NAME argument should include the desired new filename with the extension if you want to change the file extension while renaming.')
        sys.exit(1)

    root_dir = sys.argv[1]
    pattern = sys.argv[2]
    new_name = sys.argv[3]

    rename_files(root_dir, pattern, new_name)
