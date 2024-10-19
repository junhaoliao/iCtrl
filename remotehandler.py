import hashlib
import os
import sys
import threading
import datetime

import boto3
import time
from botocore.exceptions import ClientError
from botocore.exceptions import NoCredentialsError

S3_BUCKET = 'ictrl-test2024'
EXTENSION = '.clp.zst'


# Used for local file MD5 hash key calculation
def calculate_hash(file_path):
    hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash.update(chunk)
    return hash.hexdigest()


class LogNamePolicy:
    def __init__(self):
        # TODO: log type should be an input, modify this when integrating with iCtrl
        self.log_type = 'debug'

    # Create remote folder path
    def path_name(self):
        current_time = datetime.datetime.now()
        folder_path = f'logs/{current_time.year}/{current_time.month}/{current_time.day}/{self.log_type}'
        return folder_path

    # S3 object key contains remote path and remote filename
    def generate_obj_key(self, extension):
        timestamp = datetime.datetime.now()
        folder_path = f'logs/{timestamp.year}/{timestamp.month}/{timestamp.day}/{self.log_type}'
        # File name identified by time
        file_name = f'{folder_path}/ictrl_log_{timestamp.strftime("%Y-%m-%d-%H%M%S")}{extension}'
        return file_name


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
                f'\r{self.transfer} of {target} transferred '
                f'({(self.transfer / target) * 100:.2f}%).'
            )
            sys.stdout.flush()


# Handles Remote Upload logic
class RemoteHandler():
    def __init__(self, bucket, obj_key):
        self.s3 = boto3.resource('s3')
        self.s3_client = boto3.client('s3')
        self.bucket = bucket
        self.obj_key = obj_key

    # TODO: May need a method to create bucket

    # Report the time and threads use for the file upload
    def report_transfer_result(self, thread_info, reported_time):
        print(f'\nUsed {len(thread_info)} threads.')
        for ident, byte_count in thread_info.items():
            print(f'{"":4}Thread {ident} copied {byte_count} bytes.')
        print(f'Your transfer took {reported_time:.2f} seconds.')

    # Obtain all remote files in the given folder_path
    def list_remote_files(self, folder_path):
        remote_files = []
        continuation_token = None

        # Loop through paginated results
        while True:
            # Use continuation token if large bucket
            if continuation_token:
                files = self.s3_client.list_objects_v2(
                    Bucket=S3_BUCKET,
                    Prefix=folder_path,
                    ContinuationToken=continuation_token
                )
            else:
                files = self.s3_client.list_objects_v2(
                    Bucket=S3_BUCKET,
                    Prefix=folder_path
                )

            # Check if files exist in the given folder
            if 'Contents' in files:
                for obj in files['Contents']:
                    remote_files.append(obj['Key'])

            # If pagination reports more files
            if files.get('IsTruncated'):
                continuation_token = files.get('NextContinuationToken')
            else:
                break

        return remote_files

    # Upload file in the local path to the remote object key
    def transfer_upload(self, local_path, file_size):
        start_time = time.perf_counter()
        # thread_info = self.upload(local_path, file_size)
        transfer_callback = TransferCallback(file_size)
        self.s3.Bucket(self.bucket).upload_file(local_path, self.obj_key, Callback=transfer_callback)
        end_time = time.perf_counter()
        self.report_transfer_result(transfer_callback.thread_info, end_time - start_time)

    #  Compare hash key between local and remote file
    def transfer_upload_with_check(self, local_path, file_size, all_remote_files):
        local_hash = calculate_hash(local_path)

        try:
            # Iterate through all files in the remote folder path
            # Generated file name may change based on time, so compare local and remote file content only.
            # Avoid comparing file names
            for obj in all_remote_files:
                # Get the S3 object's ETag
                s3_object = self.s3_client.head_object(Bucket=self.bucket, Key=obj)
                s3_hash = s3_object['ETag'].strip('"')

                # Compare hashes
                if local_hash == s3_hash:
                    print(f'File content matches with S3 object: {obj}')
                    print('Abort Upload')
                    return

            # If no matching hash was found, upload the file
            print(f'Uploading file to {self.obj_key}')
            self.transfer_upload(local_path, file_size)

        except ClientError as e:
            print(f'Error: {e}')

    def upload_mechanism(self, local_path, file_size):
        name = LogNamePolicy()

        all_remote_files = self.list_remote_files(name.path_name())

        self.transfer_upload_with_check(local_path, file_size, all_remote_files)

    # TODO: download does not work yet
    def transfer_download(self, local_path, file_size):
        start_time = time.perf_counter()
        transfer_callback = TransferCallback(file_size)
        self.s3.Bucket(self.bucket).Object(self.obj_key).download_file(local_path, Callback=transfer_callback)
        end_time = time.perf_counter()
        self.report_transfer_result(transfer_callback.thread_info, end_time - start_time)

def main():
    local_path = os.getcwd() + '\\example.clp.zst'
    log_name = LogNamePolicy()
    obj_key = log_name.generate_obj_key(EXTENSION)

    # TODO: detect updates in examples.clp.zst and then upload

    # Test upload file in local_path
    print(f'=====Upload {local_path} Start=====')
    a = RemoteHandler(S3_BUCKET, obj_key)
    a.upload_mechanism(local_path, file_size=100)
    print(f'=====Upload {local_path} End=====')

    # Test download file in local_path
    # Download does not work yet
    '''
    download_local_path = os.path.join(os.getcwd(),'local_store').replace('\\'','/')
    print(f'=====Download {download_local_path} Start=====')
    a.transfer_download(local_path, 100)
    print(f'=====Download {download_local_path} End=====')
    '''


if __name__ == '__main__':
    try:
        main()
    except NoCredentialsError as error:
        print(error)
