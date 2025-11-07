import json
from typing import Dict, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field, root_validator

from api.services.clarity import ClarityClient


class ClarityAnalyzeInput(BaseModel):
    """Input schema for invoking the Clarity engine analyze endpoint."""

    directive: str = Field(..., description="The instruction or question for the Clarity engine.")
    domain: str = Field(
        ...,
        description=(
            "Clarity knowledge domain. Examples: legal, financial, security, "
            "healthcare, data-science, education, proposals, ngo, data-entry, expenses."
        ),
    )
    files: Dict[str, str] | None = Field(
        default=None,
        description="Optional map of file names to encoded payloads for document analysis.",
    )

    @root_validator(pre=True)
    def normalize_files(cls, values):
        files = values.get("files")
        if files and not isinstance(files, dict):
            raise ValueError("files must be a dictionary of filename -> data_url/base64.")
        return values


class ClarityAnalyzeTool(BaseTool):
    """Crew tool for delegating complex analysis work to the Clarity engine."""

    name: str = "clarity_analyze"
    description: str = (
        "Use this tool to request deep analysis from the Clarity engine across supported domains. "
        "Ideal for executive briefings, financial insights, document intelligence, policy reviews, "
        "and compliance tasks. Always supply a clear directive and correct domain."
    )
    args_schema: Type[BaseModel] = ClarityAnalyzeInput

    def _run(self, directive: str, domain: str, files: Dict[str, str] | None = None) -> str:
        client = ClarityClient()
        try:
            payload_files = None
            if files:
                payload_files = [
                    {"filename": filename, "data": data} for filename, data in files.items()
                ]
            response = client.analyze(directive=directive, domain=domain, files=payload_files)
            return json.dumps(response)
        finally:
            client.close()
