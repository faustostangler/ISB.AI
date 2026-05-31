# Disk Space Diagnosis Report
Generated on: Sun May 31 10:19:42 AM -03 2026
Target: `/home/stangler` (Excluding: `/home/stangler/gamer_d`)

## Partition Disk Usage (`df -h /home`)
```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1p2  116G  111G     0 100% /
```

## Known Cache Directory Sizes
- **UV Cache** (`/home/stangler/.uv_cache`): _Not Found_
- **NPM Cache** (`/home/stangler/.npm`): **844.02 MB**
- **Pip Cache** (`/home/stangler/.cache/pip`): _Not Found_
- **Hugging Face Cache** (`/home/stangler/.cache/huggingface`): **726.42 MB**
- **Ollama Models (default local path)** (`/home/stangler/.ollama`): **468.00 B**
- **Cargo/Rust Registry** (`/home/stangler/.cargo`): _Not Found_
- **Antigravity IDE app data (Antigravity logs/caches)** (`/home/stangler/.gemini`): **2.14 GB**
- **Standard user cache folder (~/.cache)** (`/home/stangler/.cache`): **6.10 GB**

## Top 15 Largest Home Subdirectories (excluding gamer_d)
- `Documents`: **30.10 GB**
- `.local`: **7.62 GB**
- `.cache`: **6.10 GB**
- `.config`: **5.35 GB**
- `.gemini`: **2.14 GB**
- `.vscode`: **1.24 GB**
- `.antigravity`: **1.01 GB**
- `.npm`: **844.02 MB**
- `.antigravity-ide`: **400.01 MB**
- `.nvm`: **368.09 MB**
- `snap`: **88.82 MB**
- `Pictures`: **85.53 MB**
- `Downloads`: **23.65 MB**
- `.playwright-mcp`: **9.75 MB**
- `Desktop`: **2.82 MB**

## Top 20 Largest Files (excluding gamer_d)
- `Documents/Python/GER/gercon_raw_data.db`: **8.80 GB**
- `Documents/Python/EYE.AI/models/colpaligemma-3b-pt-448-base/model-00001-of-00002.safetensors`: **4.64 GB**
- `Documents/Python/EYE.AI/.git/objects/pack/pack-2338750b9fb00f256fc87d7d0cb3636dc8baddc8.pack`: **4.34 GB**
- `.cache/whisper/large-v3.pt`: **2.35 GB**
- `.cache/whisper/medium.pt`: **1.42 GB**
- `Documents/Python/GER/gercon_consolidado.csv`: **1.22 GB**
- `Documents/Python/EYE.AI/.git/objects/pack/tmp_pack_BqB3yB`: **1.14 GB**
- `Documents/Python/EYE.AI/models/colpaligemma-3b-pt-448-base/model-00002-of-00002.safetensors`: **822.54 MB**
- `Documents/Python/GER/gercon_flatten.csv`: **807.72 MB**
- `.cache/whisper/small.pt`: **461.21 MB**
- `Documents/Python/GER/inspecao_volumetria_unicos/evolucoes_json.csv`: **394.44 MB**
- `Documents/Python/GER/gercon_consolidado.parquet`: **317.83 MB**
- `Documents/Python/GER/.git/objects/b6/59fc7fe83938ecc2d92becb9393d208284ca18`: **264.80 MB**
- `Documents/Python/GER/inspecao_volumetria_unicos/historico_evolucoes_completo.csv`: **228.76 MB**
- `.local/share/Steam/ubuntu12_64/libcef.so`: **209.28 MB**
- `.vscode/extensions/google.geminicodeassist-2.72.0/cloudcode_cli.zip`: **189.32 MB**
- `.local/share/AnkiProgramFiles/.venv/lib/python3.13/site-packages/PyQt6/Qt6/lib/libQt6WebEngineCore.so.6`: **177.27 MB**
- `.local/share/AnkiProgramFiles/cache/archive-v0/q3A4AtDuMgZskQ2NPVqLJ/PyQt6/Qt6/lib/libQt6WebEngineCore.so.6`: **177.27 MB**
- `Documents/Python/EYE.AI/models/colpali-v1.2/checkpoint-18000/optimizer.pt`: **150.09 MB**
- `Documents/Python/OAI/.venv/bin/pyrefly`: **141.60 MB**

## Docker Disk Usage (`docker system df`)
```text
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          2         0         104.3MB   0B (0%)
Containers      0         0         0B        0B
Local Volumes   17        0         12.87GB   12.87GB (100%)
Build Cache     0         0         0B        0B
```
