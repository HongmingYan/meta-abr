3
z�\�  �               @   s�   d dl mZ d dl mZ d dl mZ d dl mZ d dlmZmZmZm	Z	m
Z
 d dlmZmZ d dlmZ d dlmZ d d	lmZ d d
lmZ d dlmZ d dlZG dd� de�ZdS )�    )�absolute_import)�division)�print_function)�unicode_literals)�Struct�FetchRecord�	NewRecord�
FeedRecord�InitEmptyRecord)�core�	workspace)�LocalSession)�Dataset)�pipe)�	TaskGroup)�TestCaseNc               @   s   e Zd Zdd� ZdS )�TestLocalSessionc             C   sZ  t jd�}tdtjdddg�fdtjddd	g�f�}tdtjdd
dg�fdtjdddg�f�}t jd�� t||�}t||j� �}W d Q R X dd� }dd� }t	|�}t	|�}	t
� �0}
t|j� |d�}t||d�}t||	j� � W d Q R X tjj� }t|||� t|�}|j|� |j|
� t||d�}x.t|j� |j� �D ]\}}tjj||� �q:W d S )N�init�uid�   �   �   �valuegffffff�?g�������?g333333�?�   �   g        c             S   sf   t jd�}t jd�� t|| �}W d Q R X |j| j� | j� g|j� g� |jj| j� dd� |g|fS )N�proc1T)�blob�unsafe)r   �Net�	NameScoper   �Addr   r   �set)�rec�net�out� r%   �=/tmp/pip-install-myb_o1rl/torch/caffe2/python/session_test.pyr      s    
z2TestLocalSession.test_local_session.<locals>.proc1c             S   sf   t jd�}t jd�� t|| �}W d Q R X |jj| j� dd� |j| j� | j� g|j� g� |g|fS )N�proc2T)r   r   )r   r   r   r   r   r!   �Subr   )r"   r#   r$   r%   r%   r&   r'   '   s    
z2TestLocalSession.test_local_session.<locals>.proc2)�	processor)�ws)r   r   r   �np�arrayr   r   r
   Zclone_schemar   r   r   �reader�writerr   �CZ	Workspacer	   r   �runr   �zipZfield_blobsZtestingZassert_array_equal)�selfZinit_netZ
src_valuesZexpected_dstZ	src_blobsZ	dst_blobsr   r'   Zsrc_dsZdst_ds�tgZout1Zout2r*   �session�output�a�br%   r%   r&   �test_local_session   s4    




z#TestLocalSession.test_local_sessionN)�__name__�
__module__�__qualname__r8   r%   r%   r%   r&   r      s   r   )�
__future__r   r   r   r   Zcaffe2.python.schemar   r   r   r	   r
   Zcaffe2.pythonr   r   Zcaffe2.python.sessionr   Zcaffe2.python.datasetr   Zcaffe2.python.pipeliner   Zcaffe2.python.taskr   Zcaffe2.python.test_utilr   Znumpyr+   r   r%   r%   r%   r&   �<module>   s                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              from __future__ import absolute_import

import time
import os

from . import (LockBase, LockFailed, NotLocked, NotMyLock, LockTimeout,
               AlreadyLocked)


class LinkLockFile(LockBase):
    """Lock access to a file using atomic property of link(2).

    >>> lock = LinkLockFile('somefile')
    >>> lock = LinkLockFile('somefile', threaded=False)
    """

    def acquire(self, timeout=None):
        try:
            open(self.unique_name, "wb").close()
        except IOError:
            raise LockFailed("failed to create %s" % self.unique_name)

        timeout = timeout if timeout is not None else self.timeout
        end_time = time.time()
        if timeout is not None and timeout > 0:
            end_time += timeout

        while True:
            # Try and create a hard link to it.
            try:
                os.link(self.unique_name, self.lock_file)
            except OSError:
                # Link creation failed.  Maybe we've double-locked?
                nlinks = os.stat(self.unique_name).st_nlink
                if nlinks == 2:
                    # The original link plus the one I created == 2.  We're
                    # good to go.
                    return
                else:
                    # Otherwise the lock creation failed.
                    if timeout is not None and time.time() > end_time:
                        os.unlink(self.unique_name)
                        if timeout > 0:
                            raise LockTimeout("Timeout waiting to acquire"
                                              " lock for %s" %
                                              self.path)
                        else:
                            raise AlreadyLocked("%s is already locked" %
                                                self.path)
                    time.sleep(timeout is not None and timeout / 10 or 0.1)
            else:
                # Link creation succeeded.  We're good to go.
                return

    def release(self):
        i