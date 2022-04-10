#  Copyright (c) 2021-2022 iCtrl Developers
# 
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to
#   deal in the Software without restriction, including without limitation the
#   rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#   sell copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
# 
#  The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
# 
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#   IN THE SOFTWARE.

import os.path
import stat
from typing import Optional

import zipstream
from paramiko.sftp_client import SFTPClient

from .Connection import Connection

DL_CHUNK_SIZE = 1024 * 1024 * 4  # unit: bytes
DL_CACHE_SIZE = int(128 / 4)  # unit: count


class SFTP(Connection):
    def __init__(self):
        self.sftp: Optional[SFTPClient] = None

        super().__init__()

    def __del__(self):
        print('SFTP::__del__')
        if self.sftp is not None:
            self.sftp.close()
        super().__del__()

    def connect(self, *args, **kwargs):
        status, reason = super().connect(*args, **kwargs)
        if not status:
            return status, reason

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
                for _ in range(DL_CACHE_SIZE):
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

    def chmod(self, path, mode, recursive):
        _, _, _, stderr = self.exec_command_blocking(
            f'chmod {"-R" if recursive else ""} {"{0:0{1}o}".format(mode, 3)} "{path}"')
        stderr_lines = stderr.readlines()
        if len(stderr_lines) != 0:
            print(stderr_lines)
            return False, 'Some files were not applied with the request mode due to permission issues.'

        return True, ''

    def file(self, filename):
        f = self.sftp.file(filename, mode='w')
        f.set_pipelined(True)
        return f

    # def _rm_recurse(self, parent, file):
    #     fullpath = os.path.join(parent, file)
    #     try:
    #         self.sftp.remove(fullpath)
    #     except IOError:
    #         # it is a directory: remove any files or sub-directories under it
    #         dir_ls = self.sftp.listdir(fullpath)
    #         for dir_file in dir_ls:
    #             self._rm_recurse(fullpath, dir_file)
    #
    #         # now we can remove the emptied directory
    #         self.sftp.rmdir(fullpath)

    def rm(self, cwd, file_list):
        cmd_list = [f'cd "{cwd}" && rm -rf']
        for file in file_list:
            cmd_list.append(f'"{file}"')

        _, _, _, stderr = self.exec_command_blocking(" ".join(cmd_list))
        stderr_lines = stderr.readlines()
        if len(stderr_lines) != 0:
            print(stderr_lines)
            return False, 'Some files are not removed due to insufficient permissions'
        return True, ''

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

    def mkdir(self, cwd, name):
        _, _, _, stderr = self.exec_command_blocking(f'cd "{cwd}"&& mkdir "{name}"')
        stderr_lines = stderr.readlines()
        if len(stderr_lines) != 0:
            return False, stderr_lines[0]
        return True, ''
