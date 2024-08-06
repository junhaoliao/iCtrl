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
import posixpath
import stat
from typing import Optional

import paramiko.sftp_client
import zipstream
from paramiko.sftp_client import SFTPClient

from .Connection import Connection
import logging.config

logger = logging.getLogger(__name__)

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
        logger.debug("SFTP: Establishing SFTP connection")
        status, reason = super().connect(*args, **kwargs)
        if not status:
            logger.warning(f"SFTP: connect failed due to {reason}")
            return status, reason

        try:
            logger.debug("SFTP: Open SFTP client connection")
            self.sftp = self.client.open_sftp()
            self.sftp.chdir(".")
        except Exception as e:
            logger.warning(f"SFTP: Client connect failed due to {e}")
            return False, str(e)

        return True, ''

    def ls(self, path=""):
        try:
            if path != "":
                self.sftp.chdir(path)
            cwd = self.sftp.getcwd()
            attrs = self.sftp.listdir_attr(cwd)
            logger.debug(f"SFTP: ls {cwd}: {attrs}")

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
            logger.warning(f"SFTP: 'ls' failed due to {e}")
            return False, repr(e), []

        return True, cwd, file_list

    def reg_size(self, file):
        file_stat = self.sftp.stat(file)
        return stat.S_ISREG(file_stat.st_mode), file_stat.st_size

    def dl_generator(self, path):
        try:
            with self.sftp.file(path) as f:
                # TODO: this seems already fixed
                #  do NOT use f.prefetch(), which can cause a serious memory leak
                #  when the user stop the download and the file is very large
                f.prefetch()
                chunk = f.read(paramiko.sftp_file.SFTPFile.MAX_REQUEST_SIZE)
                while len(chunk) != 0:
                    yield chunk
                    chunk = f.read(paramiko.sftp_file.SFTPFile.MAX_REQUEST_SIZE)
        except PermissionError:
            logger.warning(f"SFTP: dl_generator Permission denied reading {path}")
            yield bytes()

    def _zip_dir_recurse(self, z, parent, file):
        fullpath = posixpath.join(parent, file)
        try:
            mode = self.sftp.stat(fullpath).st_mode
            if stat.S_ISREG(mode):
                # print(fullpath, 'is file')
                logger.debug(f"SFTP: {fullpath} is a file")
                z.write_iter(fullpath, self.dl_generator(fullpath))
            elif stat.S_ISDIR(mode):
                # print(fullpath, 'is dir')
                logger.debug(f"SFTP: {fullpath} is a directory")
                # TODO: support writing an empty directory if len(dir_ls)==0
                #  That will involve modifying the zipstream library
                dir_ls = self.sftp.listdir(fullpath)
                for dir_file in dir_ls:
                    self._zip_dir_recurse(z, fullpath, dir_file)
        except FileNotFoundError:
            # likely due to a symlink that cannot be resolved
            # do nothing for now
            logger.warning(f"SFTP: zip_dir_recurse failed on {fullpath} due to FileNotFoundError")
            return
        except PermissionError:
            logger.warning(f"SFTP: zip_dir_recurse failed on {fullpath} due to PermissionError")
            return

    def zip_generator(self, cwd, file_list):
        logger.debug(f"SFTP: zip_generator on directory: {cwd}")
        self.sftp.chdir(cwd)
        z = zipstream.ZipFile(compression=zipstream.ZIP_DEFLATED, allowZip64=True)

        for file in file_list:
            logger.debug(f"SFTP: zip_generator on file: {file}")
            self._zip_dir_recurse(z, '', file)

        return z

    def rename(self, cwd, old, new):
        try:
            self.sftp.chdir(cwd)
            self.sftp.rename(old, new)
            logger.debug(f"SFTP: Rename {old} in directory {cwd} to {new}")
        except Exception as e:
            logger.warning(f"SFTP: Rename failed due to {e}")
            return False, repr(e)

        return True, ''

    def chmod(self, path, mode, recursive):
        _, _, _, stderr = self.exec_command_blocking(
            f'chmod {"-R" if recursive else ""} {"{0:0{1}o}".format(mode, 3)} "{path}"')
        logger.debug("SFTP: Change permission on " + path + " to '{0:0{1}o}'".format(mode, 3))
        stderr_lines = stderr.readlines()
        if len(stderr_lines) != 0:
            logger.warning(f"SFTP: chmod failed due to {stderr_lines}")
            # print(stderr_lines)
            return False, 'Some files were not applied with the request mode due to permission issues.'

        return True, ''

    def file(self, filename):
        f = self.sftp.file(filename, mode='w')
        f.set_pipelined(True)
        return f

    def rm(self, cwd, file_list):
        # FIXME: clean this up
        result = ''

        cmd_list = [f'cd "{cwd}" && rm -rf']
        counter = 0
        for file in file_list:
            cmd_list.append(f'"{file}"')

            counter += 1
            if counter == 50:
                logger.debug(f"SFTP: Execute Command {' '.join(cmd_list)}")
                _, _, stderr = self.client.exec_command(" ".join(cmd_list))
                stderr_lines = stderr.readlines()
                if len(stderr_lines) != 0:
                    logger.warning(f"SFTP: rm file failed due to {stderr_lines}")
                    # print(stderr_lines)
                    result = 'Some files are not removed due to insufficient permissions'

                # reset counter
                counter = 0
                cmd_list = [f'cd "{cwd}" && rm -rf']

        logger.debug(f"SFTP: Execute Command {' '.join(cmd_list)}")
        _, _, stderr = self.client.exec_command(" ".join(cmd_list))
        stderr_lines = stderr.readlines()
        if len(stderr_lines) != 0:
            logger.warning(f"SFTP: rm file failed due to {stderr_lines}")
            # print(stderr_lines)
            result = 'Some files are not removed due to insufficient permissions'

        if result != '':
            return False, result
        return True, ''

    def mkdir(self, cwd, name):
        logger.debug(f"SFTP: Make directory {name} at {cwd}")
        _, _, _, stderr = self.exec_command_blocking(f'cd "{cwd}"&& mkdir "{name}"')
        stderr_lines = stderr.readlines()
        if len(stderr_lines) != 0:
            logger.warning(f"SFTP: mkdir {name} in {cwd} failed due to {stderr_lines}")
            return False, stderr_lines[0]
        return True, ''
