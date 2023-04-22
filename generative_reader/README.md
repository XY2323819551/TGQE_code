# QCER_GenerateReader
Part of generate reader for **TGQE**.

## 环境配置

```
conda create -n env_name python=3.8
pip install torch==1.8.1+cu111 -f https://download.pytorch.org/whl/torch_stable.html
pip install transformers==3.0.2
```

## 进行reader Inference

将pyserini的检索结果（BM25、DPR、hybrid）作为reader的输入，使用下述命令进行答案推理
```
$ python test_reader.py --model_path checkpoint_dir/my_experiment/my_model_dir/checkpoint/best_dev \
                        --eval_data eval_data.json \
                        --per_gpu_batch_size 1 \
                        --n_context 100 \
                        --name my_test \
                        --checkpoint_dir checkpoint \
```
`--model_path`所使用的checkpoint的路径.

`--eval_data`pyserini的检索结果文件.

`--per_gpu_batch_size`设置为1即可.

运行示例
```
python reader_test.py --model_path pretrained_models/nq_reader_base --eval_data download/nq/run.dpr.nq-test.hybrid.json --per_gpu_batch_size 16 --n_context 100 --name nq_base_test --write_results
```
## 其他

**修改预测答案的数量**

在FID-main/src/model.py的generate()模型中添加两个参数：

num_beams=k1 (k1>k)

num_return_sequences=k

num_beams一定要大于num_return_sequences，否则会报错。其中num_return_sequences的值即保留的top-n predictions.
