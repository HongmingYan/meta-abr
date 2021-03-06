from __future__ import absolute_import

import os
import time

from . import (LockBase, NotLocked, NotMyLock, LockTimeout,
               AlreadyLocked)


class SymlinkLockFile(LockBase):
    """Lock access to a file using symlink(2)."""

    def __init__(self, path, threaded=True, timeout=None):
        # super(SymlinkLockFile).__init(...)
        LockBase.__init__(self, path, threaded, timeout)
        # split it back!
        self.unique_name = os.path.split(self.unique_name)[1]

    def acquire(self, timeout=None):
        # Hopefully unnecessary for symlink.
        # try:
        #     open(self.unique_name, "wb").close()
        # except IOError:
        #     raise LockFailed("failed to create %s" % self.unique_name)
        timeout = timeout if timeout is not None else self.timeout
        end_time = time.time()
        if timeout is not None and timeout > 0:
            end_time += timeout

        while True:
            # Try and create a symbolic link to it.
            try:
                os.symlink(self.unique_name, self.lock_file)
            except OSError:
                # Link creation failed.  Maybe we've double-locked?
                if self.i_am_locking():
                    # Linked to out unique name. Proceed.
                    return
                else:
                    # Otherwise the lock creation failed.
                    if timeout is not None and time.time() > end_time:
                        if timeout > 0:
                            raise LockTimeout("Timeout waiting to acquire"
                                              " lock for %s" %
                                              self.path)
                        else:
                            raise AlreadyLocked("%s is already locked" %
                                                self.path)
                    time.sleep(timeout / 10 if timeout is not None else 0.1)
            else:
                # Link creation succeeded.  We're good to go.
                return

    def release(self):
        if not self.is_locked():
            raise NotLocked("%s is not locked" % self.path)
        elif not self.i_am_locking():
            raise NotMyLock("%s is locked, but not by me" % self.path)
        os.unlink(self.lock_file)

    def is_locked(self):
        return os.path.islink(self.lock_file)

    def i_am_locking(self):
        return (os.path.islink(self.lock_file)
                and os.readlink(self.lock_file) == self.unique_name)

    def break_lock(self):
        if os.path.islink(self.lock_file):  # exists && link
            os.unlink(self.lock_file)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        3
>�\dA  �               @   s^  d Z ddlZddlZddlmZmZ ddlmZ ddlm	Z	m
Z
mZmZmZ ddlmZmZmZmZmZ ddlmZ ddlmZ dd	lmZ dd
lmZmZ ddlmZ ddlm Z  er�ddl!m"Z"m#Z# ddl$m%Z% ddl&m'Z' ddlm(Z( ddl)m*Z* ej+e,�Z-dd� Z.G dd� de/�Z0G dd� de0�Z1G dd� de0�Z2G dd� de0�Z3G dd� de/�Z4dS )z)Prepares a distribution for installation
�    N)�pkg_resources�requests)�BuildEnvironment)�
is_dir_url�is_file_url�
is_vcs_url�
unpack_url�url_to_path)�DirectoryUrlHashUnsupported�HashUnpinned�InstallationError�PreviousBuildDirError�VcsHashUnsupported)�
expanduser)�MissingHashes)�
indent_log)�display_path�normalize_path)�MYPY_CHECK_RUNNING)�vcs)�Any�Optional)�InstallRequirement)�PackageFinder)�
PipSession)�RequirementTrackerc             C   s0   | j rt| �S | jr$| jjr$t| �S t| �S dS )z�Factory to make an abstract dist object.

    Preconditions: Either an editable req with a source_dir, or satisfied_by or
    a wheel link, or a non-editable req with a source_dir.

    :return: A concrete DistAbstraction.
    N)�editable�IsSDist�link�is_wheel�IsWheel)�req� r"   ��   /media/mrc/新加卷1/ubuntu_files/pytorch-maml-rl-master/venv/lib/python3.6/site-packages/pip-19.0.3-py3.6.egg/pip/_internal/operations/prepare.py�make_abstract_dist"   s
    	r$   c               @   s(   e Zd ZdZdd� Zdd� Zdd� ZdS )	�DistAbstractionay  Abstracts out the wheel vs non-wheel Resolver.resolve() logic.

    The requirements for anything installable are as follows:
     - we must be able to determine the requirement name
       (or we can't correctly handle the non-upgrade case).
     - we must be able to generate a list of run-time dependencies
       without installing any additional packages (or we would
       have to either burn time by doing temporary isolated installs
       or alternatively violate pips 'don't start installing unless
       all requirements are available' rule - neither of which are
       desirable).
     - for packages with setup requirements, we must also be able
       to determine their requirements without installing additional
       packages (for the same reason as run-time dependencies)
     - we must be able to create a Distribution object exposing the
       above metadata.
    c             C   s
   || _ d S )N)r!   )�selfr!   r"   r"   r#   �__init__F   s    zDistAbstraction.__init__c             C   s   t �dS )z Return a setuptools Dist object.N)�NotImplementedError)r&   r"   r"   r#   �distJ   s    zDistAbstraction.distc             C   s   t �dS )z3Ensure that we can get a Dist for this requirement.N)r(   )r&   �finder�build_isolationr"   r"   r#   �prep_for_distO   s    zDistAbstraction.prep_for_distN)�__name__�
__module__�__qualname__�__doc__r'   r)   r,   r"   r"   r"   r#   r%   3   s   r%   c               @   s   e Zd Zdd� Zdd� ZdS )r    c             C   s   t tj| jj��d S )Nr   )�listr   �find_distributionsr!   �
source_dir)r&   r"   r"   r#   r)   W   s    zIsWheel.distc             C   s   d S )Nr"   )r&   r*   r+   r"   r"   r#   r,   \   s    zIsWheel.prep_for_distN)r-   r.   r/   r)   r,   r"   r"   r"   r#   r    U   s   r    c               @   s   e Zd Zdd� Zdd� ZdS )r   c             C   s
   | j j� S )N)r!   �get_dist)r&   r"   r"   r#   r)   d   s    zIsSDist.distc                s  �j j�  �j jo|}� �fdd�}|r�t� �j _�j jj|�j jdd� �j jj�j j�\� }� rn|d� � |r�t	j
d�j � t	j
ddjttt|���� �j j� d	�j _�j jj� }W d Q R X �j jj|�\� }� r�|d
� � �j jj||dd� �j j�  �j j�  d S )Nc                s,   t d�j| djdd� t� �D ��f ��d S )Nz4Some build dependencies for %s conflict with %s: %s.z, c             s   s   | ]\}}d ||f V  qdS )z%s is incompatible with %sNr"   )�.0�	installedZwantedr"   r"   r#   �	<genexpr>t   s   zBIsSDist.prep_for_dist.<locals>._raise_conflicts.<locals>.<genexpr>)r   r!   �join�sorted)Zconflicting_withZconflicting_reqs)�conflictingr&   r"   r#   �_raise_conflictsp   s
    
z/IsSDist.prep_for_dist.<locals>._raise_conflicts�overlayzInstalling build dependenciesz"PEP 517/518 supported requirementsz4Missing build requirements in pyproject.toml for %s.z`The project does not specify a build backend, and pip cannot fall back to setuptools without %s.z and z#Getting requirements to build wheelzthe backend dependencies�normalzInstalling backend dependencies)r!   �load_pyproject_toml�
use_pep517r   �	build_env�install_requirements�pyproject_requires�check_requirements�requirements_to_check�logger�warningr8   �map�reprr9   �spin_message�pep517_backend�get_requires_for_build_wheel�prepare_metadata�assert_source_matches_version)r&   r*   r+   Zshould_isolater;   �missing�reqsr"   )r:   r&   r#   r,   g   s>    





zIsSDist.prep_for_distN)r-   r.   r/   r)   r,   r"   r"   r"   r#   r   b   s   r   c               @   s   e Z