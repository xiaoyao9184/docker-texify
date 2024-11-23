# cache

This folder is the cache directory for Hugging Face (HF).

When using online mode, downloaded models will be cached in this folder.

For [offline mode](https://huggingface.co/docs/transformers/main/installation#offline-mode) use, please download the models in advance and specify the model directory,
such as the `texify` model below.

The folder structure for `./cache/huggingface/hub/models--vikp--texify` is as follows.

```
.
├── blobs
│   ├── 1b3717b4b654d773f5f79c93cdc994e18dd9d0ee574ad5f9bb3f8c028b79e7b3
│   ├── 4c48133aabc13f4e5f04badd8214b294a033f85b
│   ├── 614a553895a796faf884b140cae23a04c10eda6b
│   ├── 75dad5a63711d242ad16d0e2a11e194fa073fcce
│   ├── a6344aac8c09253b3b630fb776ae94478aa0275b
│   ├── a782b2f1cdab4d0bacb2dc0f85d02c4b1e31f0bd
│   ├── aa6fa677ace60c9b55199d5db22a1dce5198c5ac
│   ├── c4eed27b2bbeb493d7fbba31feda6af5c7527246a35a96d49eaa1010f9c7e9af
│   ├── cb0af56b5c3710c1f721270799366b1ac33ea76a
│   ├── cb9e3dce4c326195d08fc3dd0f7e2eee1da8595c847bf4c1a9c78b7a82d47e2d
│   ├── ea462a33e5f84b37a56e99a304aec22a89d53670
│   └── fa625711098f8cd0b355710ff6a95c894b073d62
├── refs
│   └── main
└── snapshots
    └── ce49c1fe10842e78b8be61f9e762b85ac952807d
        ├── added_tokens.json -> ../../blobs/ea462a33e5f84b37a56e99a304aec22a89d53670
        ├── config.json -> ../../blobs/614a553895a796faf884b140cae23a04c10eda6b
        ├── generation_config.json -> ../../blobs/4c48133aabc13f4e5f04badd8214b294a033f85b
        ├── .gitattributes -> ../../blobs/a6344aac8c09253b3b630fb776ae94478aa0275b
        ├── model.safetensors -> ../../blobs/c4eed27b2bbeb493d7fbba31feda6af5c7527246a35a96d49eaa1010f9c7e9af
        ├── preprocessor_config.json -> ../../blobs/aa6fa677ace60c9b55199d5db22a1dce5198c5ac
        ├── README.md -> ../../blobs/fa625711098f8cd0b355710ff6a95c894b073d62
        ├── sentencepiece.bpe.model -> ../../blobs/cb9e3dce4c326195d08fc3dd0f7e2eee1da8595c847bf4c1a9c78b7a82d47e2d
        ├── special_tokens_map.json -> ../../blobs/a782b2f1cdab4d0bacb2dc0f85d02c4b1e31f0bd
        ├── tokenizer_config.json -> ../../blobs/75dad5a63711d242ad16d0e2a11e194fa073fcce
        ├── tokenizer.json -> ../../blobs/cb0af56b5c3710c1f721270799366b1ac33ea76a
        └── training_args.bin -> ../../blobs/1b3717b4b654d773f5f79c93cdc994e18dd9d0ee574ad5f9bb3f8c028b79e7b3

4 directories, 25 files
```

It will use `./cache/huggingface/hub/models--vikp--texify/snapshots/ce49c1fe10842e78b8be61f9e762b85ac952807d`.

For more details, refer to [up@cpu-offline/docker-compose.yml](./../docker/up@cpu-offline/docker-compose.yml).


## Pre-download for offline mode

Running in online mode will automatically download the model.

install cli

```bash
pip install -U "huggingface_hub[cli]"
```

download model

```bash
huggingface-cli download vikp/texify --repo-type model --revision main --cache-dir ./cache/huggingface/hub
```