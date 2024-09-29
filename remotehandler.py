import hashlib
import os
import sys
import threading

import boto3
import time
from botocore.exceptions import ClientError
from botocore.exceptions import NoCredentialsError


def calculate_hash(file_path):
    hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda:f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()

# Transfer Logic class
class TransferCallback:
    def __init__(self, target_size):
        self.target_size = target_size
        self.transfer = 0
        self.lock = threading.Lock()
        self.thread_info = {}

    def __call__(self, transferred_size):
        thread = threading.current_thread()
        # Lock thread and perform transfer
        with self.lock:
            self.transfer += transferred_size
            if thread.ident not in self.thread_info.keys():
                self.thread_info[thread.ident] = transferred_size
            else:
                self.thread_info[thread.ident] += transferred_size
            target = self.target_size * 1024 * 1024
            sys.stdout.write(
                f"\r{self.transfer} of {target} transferred "
                f"({(self.transfer / target) * 100:.2f}%)."
            )
            sys.stdout.flush()

# Handles Remote Upload logic
class RemoteHandler():
    def __init__(self, bucket, obj_key):
        self.s3 = boto3.resource('s3')
        self.bucket = bucket
        self.obj_key = obj_key


    # TO-DO: May need a method to create bucket

    # Upload file in the local path to the remote object key
    def transfer_upload(self, local_path, file_size):
        start_time = time.perf_counter()
        # thread_info = self.upload(local_path, file_size)
        transfer_callback = TransferCallback(file_size)
        self.s3.Bucket(self.bucket).upload_file(local_path, self.obj_key, Callback=transfer_callback)
        end_time = time.perf_counter()
        self.report_transfer_result(transfer_callback.thread_info, end_time - start_time)

    #  Compare hash key between local and remote file
    # TO-DO: Add a check to see if the same file exists first
    def transfer_upload_with_check(self, local_path, file_size):
        local_hash = calculate_hash(local_path)
        s3_client = boto3.client('s3')
        try:
            s3_object = s3_client.head_object(Bucket=self.bucket, Key=self.obj_key)
            # Entity Tag used to verify remote file integrity
            s3_hash = s3_object['ETag'].strip('"')
            if local_hash != s3_hash:
                self.transfer_upload(local_path, file_size)
            else:
                print("Local hash matches S3 hash")

        except ClientError as e:
            print("Error: {}".format(e))

    # TO-DO: download does not work yet
    def transfer_download(self, local_path, file_size):
        start_time = time.perf_counter()
        transfer_callback = TransferCallback(file_size)
        self.s3.Bucket(self.bucket).Object(self.obj_key).download_file(local_path, Callback=transfer_callback)
        end_time = time.perf_counter()
        self.report_transfer_result(transfer_callback.thread_info, end_time - start_time)

    # Report the time and threads use for the file upload
    def report_transfer_result(self, thread_info, reported_time):
        print(f"\nUsed {len(thread_info)} threads.")
        for ident, byte_count in thread_info.items():
            print(f"{'':4}Thread {ident} copied {byte_count} bytes.")
        print(f"Your transfer took {reported_time:.2f} seconds.")
def main():
    local_path = os.getcwd() + "\example.clp.zst"
    s3_bucket = "ictrl-test"

    # Upload to logs/ folder
    # TO-DO: (file naming logic) logic to differentiate log (by title, by folder, etc) for each user
    obj_key = "logs/example.clp.zst"

    # Test upload file in local_path
    print(f"=====Upload {local_path} Start=====")
    a = RemoteHandler(s3_bucket, obj_key)
    a.transfer_upload(local_path, 100)
    # a.transfer_upload_with_check(local_path, 100)
    print(f"=====Upload {local_path} End=====")

    # Test download file in local_path
    # Download does not work yet
    '''
    download_local_path = os.path.join(os.getcwd(),"local_store").replace("\\","/")
    print(f"=====Download {download_local_path} Start=====")
    a.transfer_download(local_path, 100)
    print(f"=====Download {download_local_path} End=====")
    '''

if __name__ == '__main__':
    try:
        main()
    except NoCredentialsError as error:
        print(error)
