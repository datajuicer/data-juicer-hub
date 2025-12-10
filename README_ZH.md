# Data-Juicer-Hub

面向各种预训练/微调任务的社区驱动型数据处理配方与最佳实践。

## 文档

详细配方说明请访问 [这里](https://datajuicer.github.io/data-juicer-hub/zh_CN/main/docs/RecipeGallery_CN.html)。

## 快速开始

本项目提供了多种针对不同任务的数据处理配方，你可以通过克隆此仓库并使用 `--config` 参数指定目标配方文件的本地路径来直接使用它们：

```shell
# 克隆到你本地机器上的某个位置
git clone https://github.com/datajuicer/data-juicer-hub.git
# 使用实际的本地路径运行目标配方
dj-process --config <data-juicer-hub根目录>/demo/process.yaml --dataset_path <你的数据集路径>
```

## 贡献指南

这是一个由社区驱动的仓库，欢迎你上传自己的数据处理配方！😄