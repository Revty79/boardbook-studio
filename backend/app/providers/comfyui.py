from __future__ import annotations

import copy
import json
import random
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.providers.interfaces import GeneratedImageResult, ImageGenerationProvider, ProviderError


class ComfyUIProvider(ImageGenerationProvider):
    """
    Image provider backed by a ComfyUI-compatible local API.

    Workflow expectations:
    - A workflow file in API format (File -> Export (API) in ComfyUI).
    - Configured node IDs for positive/negative prompt text and sampler seed.
    """

    name = "comfyui"

    def __init__(self) -> None:
        settings = get_settings()
        self.timeout_seconds = settings.comfyui_timeout_seconds
        self.poll_interval_seconds = settings.comfyui_poll_interval_seconds
        self.max_wait_seconds = settings.comfyui_max_wait_seconds
        self.positive_prompt_node_id = settings.comfyui_positive_prompt_node_id
        self.negative_prompt_node_id = settings.comfyui_negative_prompt_node_id
        self.sampler_node_id = settings.comfyui_sampler_node_id
        self.sampler_seed_input_name = settings.comfyui_sampler_seed_input_name
        self.save_image_node_id = settings.comfyui_save_image_node_id
        self.filename_prefix = settings.comfyui_filename_prefix
        self.api_key = settings.comfyui_api_key
        self.checkpoint_name_override = settings.comfyui_checkpoint_name

        root_dir = Path(__file__).resolve().parents[2]

        workflow_path = Path(settings.comfyui_workflow_path)
        if not workflow_path.is_absolute():
            workflow_path = root_dir / workflow_path
        self.workflow_path = workflow_path

        media_root = Path(settings.media_dir)
        if not media_root.is_absolute():
            media_root = root_dir / media_root
        self.media_root = media_root
        self.generated_dir = self.media_root / "generated"
        self.generated_dir.mkdir(parents=True, exist_ok=True)

        base_url = settings.comfyui_base_url.rstrip("/")
        if base_url.endswith("/api"):
            base_url = base_url[:-4]
        self.base_url = base_url
        self.client_id = str(uuid.uuid4())

    def generate_image(self, *, prompt: str, negative_prompt: str, seed: int | None) -> GeneratedImageResult:
        workflow = self._load_workflow()
        mutable_workflow = copy.deepcopy(workflow)
        actual_seed = seed if seed is not None else random.randint(1, 999999)
        self._apply_runtime_inputs(
            workflow=mutable_workflow,
            prompt=prompt,
            negative_prompt=negative_prompt,
            seed=actual_seed,
        )

        prompt_id = self._queue_prompt(mutable_workflow)
        image_ref = self._wait_for_output_image(prompt_id)
        image_bytes = self._download_image(image_ref)
        relative_path = self._save_generated_image(image_bytes, source_filename=image_ref.get("filename"), seed=actual_seed)

        return GeneratedImageResult(image_path=relative_path, provider=self.name, seed=actual_seed)

    def _load_workflow(self) -> dict[str, Any]:
        if not self.workflow_path.exists():
            raise ProviderError(
                f"ComfyUI workflow file not found at '{self.workflow_path}'. "
                "Export a workflow via ComfyUI 'Save (API Format)' and set COMFYUI_WORKFLOW_PATH."
            )

        try:
            raw = self.workflow_path.read_text(encoding="utf-8")
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ProviderError(f"ComfyUI workflow JSON is invalid: {exc}") from exc

        if not isinstance(parsed, dict):
            raise ProviderError("ComfyUI workflow must be a JSON object keyed by node IDs.")
        return parsed

    def _apply_runtime_inputs(
        self,
        *,
        workflow: dict[str, Any],
        prompt: str,
        negative_prompt: str,
        seed: int,
    ) -> None:
        pos_node = self._get_node(workflow, self.positive_prompt_node_id, "positive prompt")
        neg_node = self._get_node(workflow, self.negative_prompt_node_id, "negative prompt")
        sampler_node = self._get_node(workflow, self.sampler_node_id, "sampler")

        pos_inputs = self._get_inputs_dict(pos_node, "positive prompt node")
        neg_inputs = self._get_inputs_dict(neg_node, "negative prompt node")
        sampler_inputs = self._get_inputs_dict(sampler_node, "sampler node")

        if "text" not in pos_inputs:
            raise ProviderError(
                f"Positive prompt node '{self.positive_prompt_node_id}' has no 'text' input."
            )
        if "text" not in neg_inputs:
            raise ProviderError(
                f"Negative prompt node '{self.negative_prompt_node_id}' has no 'text' input."
            )
        if self.sampler_seed_input_name not in sampler_inputs:
            raise ProviderError(
                f"Sampler node '{self.sampler_node_id}' has no '{self.sampler_seed_input_name}' input."
            )

        pos_inputs["text"] = prompt
        neg_inputs["text"] = negative_prompt
        sampler_inputs[self.sampler_seed_input_name] = int(seed)

        save_node = workflow.get(self.save_image_node_id)
        if isinstance(save_node, dict):
            save_inputs = save_node.get("inputs")
            if isinstance(save_inputs, dict) and "filename_prefix" in save_inputs:
                save_inputs["filename_prefix"] = self.filename_prefix

        if self.checkpoint_name_override:
            checkpoint_node_id = self._find_node_id_by_class_type(workflow, "CheckpointLoaderSimple")
            if checkpoint_node_id is not None:
                checkpoint_node = workflow.get(checkpoint_node_id)
                if isinstance(checkpoint_node, dict):
                    checkpoint_inputs = checkpoint_node.get("inputs")
                    if isinstance(checkpoint_inputs, dict) and "ckpt_name" in checkpoint_inputs:
                        checkpoint_inputs["ckpt_name"] = self.checkpoint_name_override

    def _get_node(self, workflow: dict[str, Any], node_id: str, label: str) -> dict[str, Any]:
        node = workflow.get(node_id)
        if not isinstance(node, dict):
            fallback = self._resolve_node_by_label(workflow, label)
            if fallback is None:
                raise ProviderError(
                    f"Workflow node '{node_id}' for {label} was not found. "
                    "Update COMFYUI_*_NODE_ID settings to match your workflow."
                )
            return fallback
        return node

    def _resolve_node_by_label(self, workflow: dict[str, Any], label: str) -> dict[str, Any] | None:
        if label == "sampler":
            node_id = self._find_node_id_by_class_type(workflow, "KSampler")
            if node_id is not None:
                node = workflow.get(node_id)
                return node if isinstance(node, dict) else None
            return None

        if label in {"positive prompt", "negative prompt"}:
            text_nodes = self._find_node_ids_by_class_type(workflow, "CLIPTextEncode")
            if not text_nodes:
                return None
            # Common text2img graphs use one CLIPTextEncode for positive and one for negative.
            if label == "positive prompt":
                target_id = text_nodes[0]
            else:
                target_id = text_nodes[1] if len(text_nodes) > 1 else text_nodes[0]
            node = workflow.get(target_id)
            return node if isinstance(node, dict) else None

        return None

    def _find_node_id_by_class_type(self, workflow: dict[str, Any], class_type: str) -> str | None:
        for node_id, node in workflow.items():
            if isinstance(node, dict) and node.get("class_type") == class_type:
                return str(node_id)
        return None

    def _find_node_ids_by_class_type(self, workflow: dict[str, Any], class_type: str) -> list[str]:
        found: list[str] = []
        for node_id, node in workflow.items():
            if isinstance(node, dict) and node.get("class_type") == class_type:
                found.append(str(node_id))
        # Keep deterministic order by numeric-ish node id when possible.
        def _sort_key(item: str) -> tuple[int, str]:
            return (0, f"{int(item):08d}") if item.isdigit() else (1, item)

        found.sort(key=_sort_key)
        return found

    def _get_inputs_dict(self, node: dict[str, Any], label: str) -> dict[str, Any]:
        inputs = node.get("inputs")
        if not isinstance(inputs, dict):
            raise ProviderError(f"{label} is missing an 'inputs' object.")
        return inputs

    def _queue_prompt(self, workflow: dict[str, Any]) -> str:
        payload = {
            "prompt": workflow,
            "client_id": self.client_id,
        }
        response = self._post_json("/prompt", payload)

        prompt_id = response.get("prompt_id")
        if isinstance(prompt_id, str) and prompt_id.strip():
            return prompt_id

        error = response.get("error")
        node_errors = response.get("node_errors")
        if error:
            raise ProviderError(f"ComfyUI rejected prompt: {error}")
        if node_errors:
            raise ProviderError(f"ComfyUI node validation errors: {node_errors}")
        raise ProviderError("ComfyUI did not return a prompt_id.")

    def _wait_for_output_image(self, prompt_id: str) -> dict[str, str]:
        deadline = time.time() + self.max_wait_seconds
        last_error: str | None = None

        while time.time() < deadline:
            history = self._get_json(f"/history/{prompt_id}")
            if isinstance(history, dict):
                prompt_entry = history.get(prompt_id)
                if isinstance(prompt_entry, dict):
                    outputs = prompt_entry.get("outputs")
                    if isinstance(outputs, dict):
                        first_image = self._extract_first_image(outputs)
                        if first_image is not None:
                            return first_image

                    status = prompt_entry.get("status")
                    if isinstance(status, dict):
                        messages = status.get("messages")
                        if isinstance(messages, list):
                            for item in messages:
                                if isinstance(item, list) and item and item[0] == "execution_error":
                                    last_error = str(item)

            time.sleep(self.poll_interval_seconds)

        detail = f" ComfyUI reported: {last_error}" if last_error else ""
        raise ProviderError(
            f"Timed out waiting for ComfyUI output for prompt_id '{prompt_id}'.{detail}"
        )

    def _extract_first_image(self, outputs: dict[str, Any]) -> dict[str, str] | None:
        for node_output in outputs.values():
            if not isinstance(node_output, dict):
                continue
            images = node_output.get("images")
            if not isinstance(images, list):
                continue

            for image_info in images:
                if not isinstance(image_info, dict):
                    continue
                filename = image_info.get("filename")
                if not isinstance(filename, str) or not filename:
                    continue
                subfolder = image_info.get("subfolder", "")
                folder_type = image_info.get("type", "output")
                return {
                    "filename": filename,
                    "subfolder": str(subfolder),
                    "type": str(folder_type),
                }
        return None

    def _download_image(self, image_ref: dict[str, str]) -> bytes:
        query = urllib.parse.urlencode(
            {
                "filename": image_ref["filename"],
                "subfolder": image_ref.get("subfolder", ""),
                "type": image_ref.get("type", "output"),
            }
        )
        url = f"{self.base_url}/view?{query}"
        req = urllib.request.Request(
            url,
            headers=self._headers(),
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            raise ProviderError(f"Failed to download ComfyUI image: HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise ProviderError(
                "Unable to download image from ComfyUI /view endpoint."
            ) from exc

    def _save_generated_image(self, data: bytes, *, source_filename: str | None, seed: int) -> str:
        suffix = ".png"
        if source_filename:
            source_suffix = Path(source_filename).suffix
            if source_suffix:
                suffix = source_suffix
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        filename = f"comfy_{ts}_{seed}{suffix}"
        output_path = self.generated_dir / filename
        output_path.write_bytes(data)
        return str(output_path.relative_to(self.media_root)).replace("\\", "/")

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url=url,
            data=body,
            headers=self._headers(),
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
                data = json.loads(raw)
                if not isinstance(data, dict):
                    raise ProviderError("ComfyUI returned non-object JSON.")
                return data
        except urllib.error.HTTPError as exc:
            payload_text = ""
            try:
                payload_text = exc.read().decode("utf-8")
            except Exception:
                payload_text = ""
            detail = payload_text or f"HTTP {exc.code}"
            raise ProviderError(f"ComfyUI request failed: {detail}") from exc
        except urllib.error.URLError as exc:
            raise ProviderError(
                "Unable to reach ComfyUI. Check COMFYUI_BASE_URL and confirm ComfyUI is running."
            ) from exc
        except TimeoutError as exc:
            raise ProviderError("ComfyUI request timed out.") from exc

    def _get_json(self, path: str) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url=url, headers=self._headers(), method="GET")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
                data = json.loads(raw)
                if not isinstance(data, dict):
                    return {}
                return data
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return {}
            raise ProviderError(f"ComfyUI history request failed: HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise ProviderError(
                "Unable to query ComfyUI history endpoint."
            ) from exc
        except TimeoutError as exc:
            raise ProviderError("ComfyUI history request timed out.") from exc
        except json.JSONDecodeError:
            return {}

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers
