3
z�\#  �               @   s�   d dl mZ d dl mZ d dl mZ d dl mZ d dlmZmZ d dlj	j
Zd dlZd dlZd dlmZ eje�Zdd	� Zd
d� Zdd� Zdd� ZG dd� dej�ZdS )�    )�absolute_import)�division)�print_function)�unicode_literals)�core�	workspaceN)�givenc             C   sN   t jt j| �d dgt jd�}x*t| �D ]\}}tjdt|��\||< q(W |S )Nr   �   )�dtype�f)�np�empty�shape�float32�	enumerate�struct�unpack�	bytearray)�byte_matrix�floats�iZbyte_values� r   �W/tmp/pip-install-myb_o1rl/torch/caffe2/python/fused_8bit_rowwise_conversion_ops_test.py�bytes_to_floats   s    r   c             C   s�   t jt j| �d dgt jd�}xft| �D ]Z\}}t|t j�sHt|| f��tj	d|�}t|d t
�rpt|�||< q(ttt|��||< q(W |S )Nr   �   )r
   r   )r   r   r   �uint8r   �
isinstancer   �AssertionErrorr   �pack�int�list�map�ord)r   r   r   �value�as_bytesr   r   r   �floats_to_bytes   s    r%   c       
      C   s�   t j| ddd�}t j| ddd�}|| }|}|d }d|d  }t| | | �}t|jd��}t|jd��}	t j|||	gdd�S )	Nr	   T)�axisZkeepdimsg     �o@g:�0�yE>)r&   �����r'   )r   �min�max�round_to_nearestr%   ZreshapeZconcatenate)
�dataZminimum�maximum�span�bias�scaleZinverse_scale�quantized_dataZscale_bytesZ
bias_bytesr   r   r   �%fused_rowwise_8bit_quantize_reference%   s    r1   c             C   sh   t | �}t|d d �dd�f jtj��}t|d d �dd �f jtj��}|d d �d d�f }|| | S )N�   r   i���������r3   i����)r1   r   �astyper   r   )r+   Zfused_quantizedr/   r.   r0   r   r   r   �0fused_rowwise_8bit_quantize_dequantize_reference2   s
      r5   c               @   sD   e Zd Zeejddd�d�dd� �Zeejddd�d�dd� �ZdS )	�*TestFused8BitRowwiseQuantizationConversion�   )Zmin_dimZmax_dim)�
input_datac             C   sT   t jddgdg�}tjd|� tj|� tjd�}t|jtj	��}tj
j||� d S )N� FloatToFused8BitRowwiseQuantizedr8   r0   )r   �CreateOperatorr   �FeedBlob�RunOperatorOnce�	FetchBlobr1   r4   r   r   �testing�assert_array_almost_equal)�selfr8   �quantizer0   �	referencer   r   r   �test_quantize_op;   s    

z;TestFused8BitRowwiseQuantizationConversion.test_quantize_opc             C   s~   t jddgdg�}tjd|� tj|� tjd�}t jddgdg�}tjd|� tj|� tjd�}t|�}tjj	||� d S )Nr9   r8   r0   Z Fused8BitRowwiseQuantizedToFloat�dequantized_data)
r   r:   r   r;   r<   r=   r5   r   r>   r?   )r@   r8   rA   r0   Z
dequantizerD   rB   r   r   r   �test_quantize_and_dequantize_opL   s     



zJTestFused8BitRowwiseQuantizationConversion.test_quantize_and_dequantize_opN)�__name__�
__module__�__qualname__r   �huZtensorrC   rE   r   r   r   r   r6   :   s   r6   )�
__future__r   r   r   r   Zcaffe2.pythonr   r   Z"caffe2.python.hypothesis_test_util�pythonZhypothesis_test_utilrI   Znumpyr   r   Z
hypothesisr   Z	vectorize�roundr*   r   r%   r1   r5   ZHypothesisTestCaser6   r   r   r   r   �<module>   s   
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 