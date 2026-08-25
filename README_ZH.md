# Data-Juicer-Hub

面向 [Data-Juicer](https://github.com/datajuicer/data-juicer) 生态的社区驱动型配方、工具与资源集合。

## 目录索引

| 目录 | 说明 |
|------|------|
| [demo](demo/) | 即用型 Data-Juicer 数据处理配方（YAML 配置） |
| [juicer_playground](juicer_playground/) | [Juicer](juicer_playground/README.md) 数据精炼模型的交互式 Playground 与部署脚本 |
| [annotation_config](annotation_config/) | 标注任务配置 |
| [dataset_config](dataset_config/) | 数据集处理配置 |
| [refined_recipes](refined_recipes/) | 优化后的数据处理配方 |
| [reproduced_bloom](reproduced_bloom/) | 复现 BLOOM 数据处理的配方 |
| [reproduced_redpajama](reproduced_redpajama/) | 复现 RedPajama 数据处理的配方 |

## 文档

详细配方说明请访问[这里](https://datajuicer.github.io/data-juicer-hub/zh_CN/main/docs/RecipeGallery_CN.html)。

## 快速开始

### 数据处理配方

本项目提供了多种针对不同任务的数据处理配方，你可以通过克隆此仓库并使用 `--config` 参数指定目标配方文件的本地路径来直接使用它们：

```shell
# 克隆到你本地机器上的某个位置
git clone https://github.com/datajuicer/data-juicer-hub.git
# 使用实际的本地路径运行目标配方
dj-process --config <data-juicer-hub根目录>/demo/process.yaml --dataset_path <你的数据集路径>
```

如果你更喜欢通过交互式 Notebook 学习和使用 Data-Juicer，可以切换到 `notebook` 分支：

```shell
# 切换到 notebook 分支
git checkout notebook
```

该分支包含了 Data-Juicer 的详细 Notebook 教程，你可以参考[在线文档](https://datajuicer.github.io/data-juicer-hub/zh_CN/main/docs/NotebooksTutorial_ZH.html)进行使用。

### Juicer Playground

Juicer Playground 提供了 Juicer 数据精炼模型的交互式演示环境。详见 [juicer_playground/README.md](juicer_playground/README.md)。

## 贡献指南

这是一个由社区驱动的仓库，欢迎你上传自己的数据处理配方和工具！😄
