3
z�\�1  �               @   s�   d dl mZ d dl mZ d dl mZ d dl mZ d dlZd dlmZm	Z	m
Z
 d dlmZ dd	� Zd
d� Zdd� Zddd�ZG dd� de�ZG dd� d�ZdS )�    )�absolute_import)�division)�print_function)�unicode_literalsN)�core�	workspace�
net_drawer)�
caffe2_pb2c             C   s   t jj| dd� | jD ��S )Nc             S   s   g | ]}|d  �qS )�_grad� )�.0�sr   r   �A/tmp/pip-install-myb_o1rl/torch/caffe2/python/gradient_checker.py�
<listcomp>   s    z$getGradientForOp.<locals>.<listcomp>)r   ZGradientRegistryZGetGradientForOp�output)�opr   r   r   �getGradientForOp   s    r   c             C   s^   | | }t |tj�rtj| S t |tj�s.t�d}tjd|j|j	|g|�}tj
|� tj| S )NZtmp_dense_gradZSparseToDense)�
isinstancer   ZBlobRefe