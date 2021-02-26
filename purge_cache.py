import glob
import os

def main():
    cache_files = glob.glob('data/*.json')
    deleted_file_count = 0

    for file in cache_files:
        print('Deleting file: ', file)
        os.remove(file)
        deleted_file_count += 1

    print('Deleted file count: ', deleted_file_count)

main()
