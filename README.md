Docling External Plugin: Picture Description API (env-based)
Repository name: docling-picture-description-plugin

Overview
This plugin extends Docling to describe pictures in PDFs using an OpenAI-compatible API. It returns concise text per detected picture and can optionally include token usage from the backend response. Configuration is done via environment variables (no hard-coded secrets).

Key points
- Environment-driven setup (.env with .env.example).
- Works with Azure OpenAI or any OpenAI-compatible server (vLLM, custom gateways, etc.).
- Clear end-to-end example in test.py.

Quick start
- (Optional) Create/activate a virtual environment
  - python -m venv .venv
  - source .venv/bin/activate  # macOS/Linux
- Install
  - pip install -e .
  - pip install -r requirements.txt
- Configure
  - cp .env.example .env
  - Edit .env and set your keys
- Run
  - python test.py

Configuration (choose one backend)

Azure OpenAI (recommended)
- AZURE_OPENAI_ENDPOINT       e.g., https://YOUR_RESOURCE_NAME.openai.azure.com
- AZURE_OPENAI_API_KEY        your Azure key
- AZURE_OPENAI_DEPLOYMENT     e.g., gpt-4o-mini
- AZURE_OPENAI_API_VERSION    e.g., 2025-01-01-preview

OpenAI-compatible server (used if not all Azure vars are present)
- OPENAI_COMPATIBLE_API_URL            default: http://localhost:8000/v1/chat/completions
- OPENAI_COMPATIBLE_API_KEY            optional; sent as a header if provided
- OPENAI_COMPATIBLE_API_HEADER_NAME    default: api-key
  - For Bearer tokens, set header name to Authorization and key to Bearer YOUR_TOKEN

Optional behavior
- PICTURE_DESCRIPTION_PROMPT           default: Describe the image in three sentences. Be concise and accurate.
- PICTURE_DESCRIPTION_TIMEOUT          default: 90
- PICTURE_DESCRIPTION_TOKEN_EXTRACT_KEY default: usage (set empty if unsupported)
- SOURCE_DOCUMENT                      default: https://arxiv.org/pdf/2408.09869 (URL or local path)

How it works (test.py)
- Loads .env via python-dotenv.
- Resolves backend:
  - If all AZURE_* are set → uses Azure OpenAI.
  - Else → uses the OpenAI-compatible URL/header.
- Builds options (url, headers, params, prompt, timeout, token_extract_key).
- Configures Docling PdfPipelineOptions:
  - allow_external_plugins = True
  - enable_remote_services = True
  - do_picture_description = True
  - generate_picture_images = True
- Runs conversion and prints:
  - Markdown of the document.
  - Token usage per picture (if provided by backend).

Project structure
- pyproject.toml                         packaging and Docling entry point
- docling/__init__.py                    namespace to augment installed docling
- docling/api_usage.py                   registers the plugin (picture_description())
- docling/picture_description_api_model_with_token.py  options type
- docling/api_image_request_with_token.py HTTP helper for image+prompt → text (+ usage)
- docling/picture_description_api_model.py model that attaches DescriptionAnnotationWithToken
- test.py                                environment-driven example

Plugin registration
- Entry point in pyproject.toml:
  [project.entry-points."docling"]
  "api_usage" = "docling.api_usage"
- The module docling.api_usage must define:
  def picture_description():
      return {"picture_description": [PictureDescriptionApiModelWithToken]}

Troubleshooting
- Plugin not loading:
  - Ensure allow_external_plugins=True and the package is installed in the same venv as Docling.
  - Check entry_points in your venv (dist-info): it should include [docling] api_usage = docling.api_usage.
- Only default classes registered:
  - picture_description() must return the MODEL CLASS (not the options class).
  - Entry point must target the module (docling.api_usage).
- API calls failing:
  - Confirm enable_remote_services=True.
  - Verify URL, API key, and header name in .env.
  - For Azure, check endpoint, deployment, and API version.
- Token usage missing:
  - Your backend may not return usage; TOKEN_EXTRACT_KEY can be empty.

Security
- Do not commit .env; use .gitignore to exclude local secrets.

References
- Docling plugin concepts: https://docling-project.github.io/docling/concepts/plugins/
- OCR factory docs: https://docling-project.github.io/docling/concepts/plugins/#ocr-factory
# custom-docling-plugins
