import os.path
import stat
from typing import Optional

import zipstream
from paramiko.sftp_client import SFTPClient

from application.Connection import Connection

DL_CHUNK_SIZE = 1024 * 1024 * 4  # unit: bytes


class SFTP(Connection):
    def __init__(self):
        self.sftp: Optional[SFTPClient] = None

        super().__init__()

    def __del__(self):
        print('SFTP::__del__')
        self.sftp.close()
        super().__del__()

    def connect(self, *args, **kwargs):
        super().connect(*args, **kwargs)

        try:
            self.sftp = self.client.open_sftp()
            self.sftp.chdir(".")
        except Exception as e:
            return False, str(e)

        return True, ''

    def ls(self, path=""):
        try:
            if path != "":
                self.sftp.chdir(path)
            cwd = self.sftp.getcwd()
            attrs = self.sftp.listdir_attr(cwd)

            file_list = []
            # TODO: should support uid and gid later
            for file_attr in attrs:
                file = {
                    "id": file_attr.filename,
                    "mode": file_attr.st_mode,
                    "size": file_attr.st_size,
                    "atime": file_attr.st_atime,
                    "mtime": file_attr.st_mtime
                }
                file_list.append(file)
        except Exception as e:
            return False, repr(e), []

        return True, cwd, file_list

    def reg_size(self, file):
        file_stat = self.sftp.stat(file)
        return stat.S_ISREG(file_stat.st_mode), file_stat.st_size

    def dl_generator(self, path):
        with self.sftp.file(path) as f:
            # do NOT use f.prefetch(), which can cause a serious memory leak
            #  when the user stop the download and the file is very large
            # Instead, we cache the file with a sliding window of size (4 * DL_CHUNK_SIZE)
            file_size = f.stat().st_size
            offset = 0
            while file_size > 0:
                read_chunks = []
                for _ in range(4):
                    if file_size <= 0:
                        break
                    chunk_size = min(file_size, DL_CHUNK_SIZE)
                    read_chunks.append((offset, chunk_size))
                    offset += chunk_size
                    file_size -= chunk_size
                for c in f.readv(read_chunks):
                    yield c

    def _zip_dir_recurse(self, z, parent, file):
        fullpath = os.path.join(parent, file)
        mode = self.sftp.stat(fullpath).st_mode
        if stat.S_ISREG(mode):
            # print(fullpath, 'is file')
            z.write_iter(fullpath, self.dl_generator(fullpath))
        elif stat.S_ISDIR(mode):
            # print(fullpath, 'is dir')
            # TODO: support writing an empty directory if len(dir_ls)==0
            #  That will involve modifying the zipstream library
            dir_ls = self.sftp.listdir(fullpath)
            for dir_file in dir_ls:
                self._zip_dir_recurse(z, fullpath, dir_file)

    def zip_generator(self, cwd, file_list):
        self.sftp.chdir(cwd)
        z = zipstream.ZipFile(compression=zipstream.ZIP_DEFLATED, allowZip64=True)

        for file in file_list:
            self._zip_dir_recurse(z, '', file)

        return z

    def rename(self, cwd, old, new):
        try:
            self.sftp.chdir(cwd)
            self.sftp.rename(old, new)
        except Exception as e:
            return False, repr(e)

        return True, ''

    def file(self, filename):
        return self.sftp.file(filename, mode='w')

    # TODO: might use this if the server is running locally
    # def dl_direct(self, path):
    #     home = os.path.expanduser("~")
    #     local_path = os.path.join(home, "Downloads", os.path.basename(path))
    #     start_time = time.time()
    #
    #     def byte_count(transferred, total):
    #         time_elapsed = time.time() - start_time
    #         print(transferred/1024/1024/time_elapsed, "MB/s")
    #
    #     self.sftp.get(path, local_path, byte_count)
