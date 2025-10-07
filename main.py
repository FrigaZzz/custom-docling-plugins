"""
Example: Docling pipeline with external picture description plugin using environment variables.

This example avoids hard-coded secrets and supports two backends:
- Azure OpenAI (recommended): set AZURE_* variables in a .env file
- OpenAI-compatible API (e.g., local vLLM or custom gateway): set OPENAI_COMPATIBLE_* variables

Setup:
1) Copy .env.example to .env and fill in the values
2) pip install -e .  (in the same venv as docling)
3) pip install -r requirements.txt  (to ensure python-dotenv is available)
4) python test.py
"""

import os
from typing import Dict, Tuple

from dotenv import load_dotenv

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling.picture_description_api_model_with_token import (
    PictureDescriptionApiOptionsWithToken,
)


def _parse_timeout(env_val: str | None, default: float = 90.0) -> float:
    if not env_val:
        return default
    try:
        return float(env_val)
    except (TypeError, ValueError):
        return default


def _resolve_backend() -> Tuple[str, Dict[str, str], str]:
    """
    Decide which backend to use based on environment variables.

    Returns:
        (url, headers, provider_name)
        provider_name in {"azure", "openai-compatible"}
    """
    # Azure OpenAI config
    az_key = os.getenv("AZURE_OPENAI_API_KEY")
    az_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    az_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    az_version = os.getenv("AZURE_OPENAI_API_VERSION")

    if az_key and az_endpoint and az_deployment and az_version:
        url = (
            f"{az_endpoint.rstrip('/')}/openai/deployments/"
            f"{az_deployment}/chat/completions?api-version={az_version}"
        )
        headers = {"api-key": az_key}
        return url, headers, "azure"

    # Fallback: generic OpenAI-compatible API
    url = os.getenv("OPENAI_COMPATIBLE_API_URL", "http://localhost:8000/v1/chat/completions")
    key = os.getenv("OPENAI_COMPATIBLE_API_KEY")
    header_name = os.getenv("OPENAI_COMPATIBLE_API_HEADER_NAME", "api-key")
    headers = {header_name: key} if key else {}
    return url, headers, "openai-compatible"


def build_picture_description_options() -> PictureDescriptionApiOptionsWithToken:
    prompt = os.getenv(
        "PICTURE_DESCRIPTION_PROMPT",
        "Describe the image in three sentences. Be concise and accurate.",
    )
    timeout = _parse_timeout(os.getenv("PICTURE_DESCRIPTION_TIMEOUT"), default=90.0)

    # default key for OpenAI-compatible APIs
    token_extract_key = os.getenv("PICTURE_DESCRIPTION_TOKEN_EXTRACT_KEY") or "usage" 
    # Normalize empty string to None
    token_extract_key = token_extract_key or None

    url, headers, provider = _resolve_backend()

    # Minimal, provider-agnostic params dict (extend if your backend needs extra query/body params)
    params: Dict[str, object] = {}

    print("Picture description backend selected:")
    print(f"  provider: {provider}")
    print(f"  url: {url}")
    print(f"  header names: {list(headers.keys())} (values hidden)")
    print(f"  timeout: {timeout}s")
    if token_extract_key:
        print(f"  token_extract_key: {token_extract_key}")

    return PictureDescriptionApiOptionsWithToken(
        url=url,
        headers=headers,
        params=params,
        prompt=prompt,
        timeout=timeout,
        token_extract_key=token_extract_key,
    )


def main():
    # Load environment variables from .env if present
    load_dotenv()

    # Configure pipeline options
    pipeline_options = PdfPipelineOptions()
    pipeline_options.allow_external_plugins = True

    # Enable image processing for paginated PDF processing
    pipeline_options.generate_picture_images = True
    pipeline_options.images_scale = 2  # Higher resolution for better quality
    pipeline_options.do_picture_description = True

    # Enable remote services (required for external API calls)
    pipeline_options.enable_remote_services = True

    # Configure picture description via env-backed options
    pipeline_options.picture_description_options = build_picture_description_options()

    # Create converter with the configured options
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    # Convert the document (local path or URL)
    source = os.getenv("SOURCE_DOCUMENT", "https://arxiv.org/pdf/2408.09869")
    print(f"\nConverting source: {source}\n")

    result = converter.convert(source)
    doc = result.document

    # Print the markdown result
    print(doc.export_to_markdown())

    # Print token usage for each picture annotation (if provided by backend)
    for idx, pic in enumerate(doc.pictures):
        print(f"\nPicture #{idx}:")
        # If PictureItem has provenance or other identifying info, print it
        try:
            prov_info = pic.prov[0] if getattr(pic, "prov", None) else None
        except (AttributeError, IndexError):
            prov_info = None
        if prov_info is not None:
            print(f"  provenance: page={prov_info.page_no} bbox={prov_info.bbox}")

        if not getattr(pic, "annotations", None):
            print("  (no annotations)")
            continue

        for ann_idx, ann in enumerate(pic.annotations):
            token_usage = getattr(ann, "token_usage", None)
            ann_text = getattr(ann, "text", None)
            print(f"  Annotation {ann_idx}: text={repr(ann_text)} token_usage={repr(token_usage)}")


if __name__ == "__main__":
    main()
