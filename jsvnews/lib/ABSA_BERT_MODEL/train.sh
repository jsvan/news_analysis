#!/usr/bin/env bash
# "python main.py --model_type bert --absa_type linear --tfm_mode finetune --fix_tfm 0 " \
#              "--model_name_or_path bert-base-uncased --data_dir ./data/rest15 --task_name rest15 " \
#              "--per_gpu_train_batch_size %s --per_gpu_eval_batch_size 8 --learning_rate 2e-5 " \
#              "--max_steps 1500 --warmup_steps 0 --do_train --do_eval --do_lower_case " \
#              "--seed %s --tagging_schema BIEOS --overfit 0 " \
#              "--overwrite_output_dir --eval_all_checkpoints --MASTER_ADDR localhost --MASTER_PORT 28512" % (
#        model_type, absa_type, tfm_mode, fix_tfm, task_name, task_name, train_batch_size, warmup_steps, seed, overfit)
# model_type = 'bert'
#absa_type = 'linear'
#tfm_mode = 'finetune'
#fix_tfm = 0
#task_name = 'rest15'
#warmup_steps = 0
#overfit = 0

TASK_NAME=commonsents
#ABSA_TYPE=tfm
ABSA_TYPE=linear
CUDA_VISIBLE_DEVICES=0 python main.py --model_type bert \
                         --absa_type ${ABSA_TYPE} \
                         --tfm_mode finetune \
                         --fix_tfm 0 \
                         --model_name_or_path bert-base-uncased \
                         --data_dir .\\data\\${TASK_NAME} \
                         --task_name ${TASK_NAME} \
                         --per_gpu_train_batch_size 8 \
                         --per_gpu_eval_batch_size 4 \
                         --learning_rate 2e-5 \
                         --do_train \
                         --do_eval \
                         --do_lower_case \
                         --tagging_schema OT \
                         --overfit 0 \
                         --overwrite_output_dir \
                         --eval_all_checkpoints \
                         --MASTER_ADDR localhost \
                         --MASTER_PORT 28512 \
                         --max_steps 1500
