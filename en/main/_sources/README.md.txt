# Data-Juicer-Hub

Community-driven recipes, tools, and resources for the [Data-Juicer](https://github.com/datajuicer/data-juicer) ecosystem.

## What's Inside

| Directory | Description |
|-----------|-------------|
| [demo](demo/) | Ready-to-use Data-Juicer processing recipes (YAML configs) |
| [juicer_playground](juicer_playground/) | Interactive playground & deployment scripts for the [Juicer](juicer_playground/README.md) data-refinement model |
| [annotation_config](annotation_config/) | Annotation task configurations |
| [dataset_config](dataset_config/) | Dataset processing configurations |
| [refined_recipes](refined_recipes/) | Refined data processing recipes |
| [reproduced_bloom](reproduced_bloom/) | Recipes for reproducing BLOOM data processing |
| [reproduced_redpajama](reproduced_redpajama/) | Recipes for reproducing RedPajama data processing |

## Documentation

Detailed documentation about the recipes can be found [here](https://datajuicer.github.io/data-juicer-hub/en/main/docs/RecipeGallery.html).

## Quick Start

### Data Processing Recipes

There are plenty of prepared recipes for data processing on different tasks. You can make use of them by cloning this repo and set the `--config` with the local path of the target recipe file:
```shell
# clone this repo to somewhere on your local machine
git clone https://github.com/datajuicer/data-juicer-hub.git
# run with the actual local path to the target recipe
dj-process --config <root-of-data-juicer-hub>/demo/process.yaml --dataset_path <your-dataset-path>
```

If you prefer learning and using Data-Juicer through interactive Notebooks, you can switch to the `notebook` branch:

```shell
# Switch to the notebook branch
git checkout notebook
```

This branch contains detailed Data-Juicer Notebook tutorials. You can refer to the [online documentation](https://datajuicer.github.io/data-juicer-hub/en/main/docs/NotebooksTutorial.html) for usage guidance.

### Juicer Playground

The Juicer Playground provides an interactive demo for the Juicer data-refinement model. See [juicer_playground/README.md](juicer_playground/README.md) for setup and usage.

## Contributing

This is a community-driven repo, so feel free to upload your own recipes and tools! 😄
