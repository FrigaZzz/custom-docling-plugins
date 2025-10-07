# Custom Docling Plugins: Picture Description API (env-based example)

Repository: https://github.com/FrigaZzz/custom-docling-plugins

This repository is a concise example of implementing Docling’s external plugin mechanism using Python packaging entry points. It follows the Docling plugin concepts and demonstrates registration via setup/packaging configuration as documented here:
- Plugin concepts: https://docling-project.github.io/docling/concepts/plugins/
- Packaging and registration (setup.py/pyproject): https://docling-project.github.io/docling/concepts/plugins/#setuppy

The plugin adds picture description to PDFs by calling an OpenAI-compatible API. For each detected image, it returns a concise textual description and, if available, token usage from the backend response. Configuration is fully environment-based—no hard-coded secrets.

## Features
- Env-driven configuration via `.env` (with `.env.example` provided).
- Supports Azure OpenAI or any OpenAI-compatible server (vLLM, custom gateways, etc.).
- End-to-end runnable example in `test.py`.
- Captures per-picture token usage when provided by the backend.

## Prerequisites
- Python 3.10+ recommended
- A working Docling installation (this package augments Docling via entry points)

## Quick start
```bash
# (Optional) create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux

# Install this plugin (editable mode) and dependencies
pip install -e .
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set your keys and settings

# Run the example
python test.py
```

## Configuration (choose one backend)

### Azure OpenAI (recommended)
Set the following variables in `.env`:
```bash
AZURE_OPENAI_ENDPOINT=https://YOUR_RESOURCE_NAME.openai.azure.com
AZURE_OPENAI_API_KEY=YOUR_AZURE_API_KEY
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2025-01-01-preview
```

### OpenAI-compatible server (used if not all Azure vars are present)
```bash
# Default URL can be adjusted to your server
OPENAI_COMPATIBLE_API_URL=http://localhost:8000/v1/chat/completions

# Optional API key; if provided, it will be sent as a header
OPENAI_COMPATIBLE_API_KEY=YOUR_API_KEY

# Header name to use for the API key (default: api-key)
# For Bearer tokens, set to Authorization and key value to "Bearer YOUR_TOKEN"
OPENAI_COMPATIBLE_API_HEADER_NAME=api-key
```

### Optional behavior
```bash
# Prompt used for describing images
PICTURE_DESCRIPTION_PROMPT="Describe the image in three sentences. Be concise and accurate."

# Request timeout in seconds
PICTURE_DESCRIPTION_TIMEOUT=90

# Key under which token usage is returned by the backend (leave empty if unsupported)
PICTURE_DESCRIPTION_TOKEN_EXTRACT_KEY=usage

# Source document to convert; can be local path or URL
SOURCE_DOCUMENT=https://arxiv.org/pdf/2408.09869
```

## How it works (test.py)
- Loads environment variables via `python-dotenv`.
- Resolves backend:
  - If all `AZURE_*` variables are set → uses Azure OpenAI.
  - Otherwise → uses the OpenAI-compatible URL and header specified in `.env`.
- Builds `PictureDescriptionApiOptionsWithUsage` with `url`, `headers`, `params`, `prompt`, `timeout`, `token_extract_key`.
- Configures `Docling PdfPipelineOptions`:
  - `allow_external_plugins = True`
  - `enable_remote_services = True`
  - `do_picture_description = True`
  - `generate_picture_images = True`
- Runs conversion and prints:
  - Markdown output of the document.
  - Token usage per picture annotation if provided by the backend.

## Project structure
- `pyproject.toml` — packaging metadata and Docling entry point.
- `docling/__init__.py` — namespace package setup to augment installed `docling`.
- `docling/api_usage.py` — plugin module exposing `picture_description()`.
- `docling/picture_description_api_model_with_usage.py` — options type (url, headers, params, prompt, timeout, concurrency, token_extract_key, etc.).
- `docling/api_image_request_with_usage.py` — HTTP helper for image+prompt → text (+ usage).
- `docling/picture_description_api_model.py` — model using the helper; attaches `DescriptionAnnotationWithUsage` containing text and `token_usage`.
- `test.py` — environment-driven example script.

## Plugin registration
Docling discovers external plugins via Python entry points. This repo registers the plugin under the `docling` group.

pyproject entry point:
```toml
[project.entry-points."docling"]
"api_usage_plugin" = "docling.api_usage_plugin"
```

The module `docling.api_usage` must define:
```python
def picture_description():
    return {"picture_description": [PictureDescriptionApiModelWithUsage]}
```

This aligns with Docling’s recommended setup described in:
- Packaging and registration docs (setup.py/pyproject): https://docling-project.github.io/docling/concepts/plugins/#setuppy

## Troubleshooting
- Plugin not loading:
  - Ensure `allow_external_plugins=True` and the package is installed in the same venv as Docling.
  - Check `dist-info/entry_points.txt` in your venv; it should include:
    ```
    [docling]
    api_usage = docling.api_usage
    ```
- Only default classes registered:
  - Ensure `picture_description()` returns the MODEL CLASS (not the options class).
  - Ensure the entry point targets the module (`docling.api_usage`), not a function path.
- API calls failing:
  - Confirm `enable_remote_services=True`.
  - Verify URL, API key, and header name in `.env`.
  - For Azure, ensure endpoint, deployment, and API version are correct.
- Token usage missing:
  - Your backend may not return usage; `PICTURE_DESCRIPTION_TOKEN_EXTRACT_KEY` can be empty if unsupported.

## Security
- Do not commit `.env`. Use `.gitignore` to exclude local secrets and other artifacts.

## References
- Docling plugin concepts: https://docling-project.github.io/docling/concepts/plugins/
- Packaging/registration via setup/pyproject: https://docling-project.github.io/docling/concepts/plugins/#setuppy
- OCR factory docs: https://docling-project.github.io/docling/concepts/plugins/#ocr-factory
