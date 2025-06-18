import os
import tarfile
import gzip
import shutil


# Folder to save all generated .tar.gz files
SOURCE_DIR = r'C:\Users\lidor\OneDrive\Desktop\test\planet'

# Number of .tar.gz files to create
NUM_ARCHIVES = 20

for i in range(1, NUM_ARCHIVES + 1):
    print(f"\n🔁 Creating archive {i}/{NUM_ARCHIVES}")

    # Step 1: Create a folder and a large dummy file
    folder_name = f"test_folder_{i}"
    test_folder = os.path.join(SOURCE_DIR, folder_name)
    os.makedirs(test_folder, exist_ok=True)

    print(f"Creating dummy file for {folder_name} (~1GB)...")
    large_file_path = os.path.join(test_folder, f"big_dummy_file_{i}.bin")
    with open(large_file_path, 'wb') as f:
        f.seek(1024 * 1024 * 1024 - 1)  # 1GB minus 1 byte
        f.write(b'\0')

    # Step 2: Create .tar archive
    tar_path = os.path.join(SOURCE_DIR, f"{folder_name}.tar")
    print(f"Creating .tar archive for {folder_name}...")
    with tarfile.open(tar_path, 'w') as tar:
        tar.add(test_folder, arcname=folder_name)

    # Step 3: Compress to .tar.gz
    gz_path = tar_path + '.gz'
    print(f"Compressing to {gz_path}...")
    with open(tar_path, 'rb') as f_in:
        with gzip.open(gz_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    # Step 4: Cleanup
    print(f"Cleaning up files for {folder_name}...")
    os.remove(tar_path)
    shutil.rmtree(test_folder)

    print(f"✅ Done: {gz_path}")