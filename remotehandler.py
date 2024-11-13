import hashlib
import os
import sys
import threading
import datetime
import base64

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

def calculate_sha256_hash(file_path):
    hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash.update(chunk)
    return hash.hexdigest()

class LogNamePolicy:

    # Create remote folder path
    def path_name(self):
        current_time = datetime.datetime.now()
        folder_path = f'logs/{current_time.year}/{current_time.month}/{current_time.day}'
        return folder_path

    # S3 object key contains remote path and remote filename
    def generate_obj_key(self, extension):
        timestamp = datetime.datetime.now()
        folder_path = f'logs/{timestamp.year}/{timestamp.month}/{timestamp.day}'
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
        self.multipart_upload = {
            'size': 1024 * 1024 * 5,  # 5KB for testing purpose
            'index': 1,
            'pos': 0,
            'uploaded parts': []
        }

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
    def compare_local_and_remote_files(self, local_path, all_remote_files):

        try:
            # Iterate through all files in the remote folder path
            # Generated file name may change based on time, so compare local and remote file content only.
            # Avoid comparing file names
            for obj in all_remote_files:
                # Get the S3 object's ETag
                s3_object = self.s3_client.head_object(Bucket=self.bucket, Key=obj)
                print(s3_object)

                # If SHA256 hash key exist on remote
                if 'ChecksumSHA256' in s3_object:
                    print('Checking SHA256 values of file')
                    s3_hash = s3_object['ChecksumSHA256'].strip('"')
                    # Compare SHA256 hash key
                    if calculate_sha256_hash(local_path) == s3_hash:
                        print(f'File content matches with S3 object: {obj}')
                        print('Abort Upload')
                        return False

                # Use MD5 (default) hash key if SHA256 hash key does not exist
                else:
                    print('Checking MD5 values of file')
                    s3_hash = s3_object['ETag'].strip('"')

                    # Compare ETag with MD5 hashes
                    if calculate_hash(local_path) == s3_hash:
                        print(f'File content matches with S3 object: {obj}')
                        print('Abort Upload')
                        return False

            return True


        except ClientError as e:
            print(f'Error: {e}')
            return False

    def transfer_upload_from_pos(self, local_path, upload_id):
        with open(local_path, 'rb') as f:
            f.seek(self.multipart_upload['pos'])
            upload_data = f.read(self.multipart_upload['size'])

        print('Part Number: ', self.multipart_upload['index'])
        response = self.s3_client.upload_part(Bucket=self.bucket, Key=self.obj_key, Body=upload_data,
                                              PartNumber=self.multipart_upload['index'], UploadId=upload_id)


        # Report unique part number and associated entity tag
        return {'PartNumber': self.multipart_upload['index'], 'ETag': response['ETag']}

    def transfer_multipart_upload(self, local_path):
        # Request to initiate a multipart upload to obtain upload ID
        response = self.s3_client.create_multipart_upload(Bucket=self.bucket, Key=self.obj_key)
        upload_id = response['UploadId']
        print(f'Upload starting...\n')

        try:
            file_growth_counter = 0
            while True:
                file_size = os.path.getsize(local_path)

                # Upload once the file exceeds set size
                if file_size - self.multipart_upload['pos'] >= self.multipart_upload['size']:
                    response = self.transfer_upload_from_pos(local_path, upload_id)
                    self.multipart_upload['index'] += 1
                    self.multipart_upload['pos'] += self.multipart_upload['size']
                    print(response)

                    # AWS S3 Part number restriction
                    if self.multipart_upload['index'] < 1 or self.multipart_upload['index'] > 10000:
                        # TODO: Need to start a new multipart upload session here
                        break
                    self.multipart_upload['uploaded parts'].append(response)
                    file_growth_counter = 0
                # Pause if the file is not growing
                elif os.path.getsize(local_path) == file_size:
                    time.sleep(10)  # Wait 10 seconds to check if the file size is updated
                    file_growth_counter += 1

                # If file does not grow within a set period of time
                if file_growth_counter >= 3:
                    break

            # Concatenate the parts in ascending part number order
            response = self.s3_client.complete_multipart_upload(
                Bucket=self.bucket,
                Key=self.obj_key,
                UploadId=upload_id,
                MultipartUpload={
                    'Parts': [
                        {
                            'PartNumber': part['PartNumber'],
                            'ETag': part['ETag']
                        }
                        for part in self.multipart_upload['uploaded parts']
                    ]
                }
            )
            print(f'Upload successful. Uploaded {self.multipart_upload["index"]-1} segments.')
            return response
        except Exception as e:
            print('Upload aborted.', e)
            self.s3_client.abort_multipart_upload(Bucket=self.bucket, Key=self.obj_key, UploadId=upload_id)

    def multipart_upload_mechanism(self, local_path):
        name = LogNamePolicy()
        all_remote_files = self.list_remote_files(name.path_name())

        ret = self.compare_local_and_remote_files(local_path, all_remote_files)
        if ret:
            # If no matching hash was found, upload the file
            print(f'Uploading file to {self.obj_key}')
            self.transfer_multipart_upload(local_path)

    def upload_mechanism(self, local_path, file_size):
        name = LogNamePolicy()

        all_remote_files = self.list_remote_files(name.path_name())

        ret = self.compare_local_and_remote_files(local_path, all_remote_files)
        if ret:
            # If no matching hash was found, upload the file
            print(f'Uploading file to {self.obj_key}')
            self.transfer_upload(local_path, file_size)



def main():
    local_path = os.getcwd() + '\\testfile'
    log_name = LogNamePolicy()
    obj_key = log_name.generate_obj_key(EXTENSION)


    # Test upload file in local_path
    '''
    print(f'=====Upload {local_path} Start=====')
    a = RemoteHandler(S3_BUCKET, obj_key)
    a.upload_mechanism(local_path, file_size=100)
    print(f'=====Upload {local_path} End=====')
    '''


    print(f'=====Multipart Upload {local_path} Start=====\n')
    upload_inst = RemoteHandler(S3_BUCKET, obj_key)
    upload_inst.multipart_upload_mechanism(local_path)
    print(f'=====Multipart Upload {local_path} End=====\n')


if __name__ == '__main__':
    try:
        main()
    except NoCredentialsError as error:
        print(error)
