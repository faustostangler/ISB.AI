import argparse
import json
import pathlib
import sys

from fastapi import FastAPI
from pydantic import BaseModel, Field

from isb.config import settings

# Initialize FastAPI application
app = FastAPI(
    title="Intelligent Second Brain (ISB.AI)",
    description="API Presentation layer for the ISB.AI Modular Monolith",
    version="0.1.0",
    debug=settings.DEBUG,
)


class HealthCheckResponse(BaseModel):
    """Schema representing the application health status response."""

    status: str = Field(..., description="The status of the application, typically 'healthy'")


@app.get("/health", tags=["Lifecycle"], response_model=HealthCheckResponse)
def health_check() -> HealthCheckResponse:
    """Performs a simple readiness check of the FastAPI presentation node.

    Returns:
        HealthCheckResponse: The health check status response model.
    """
    return HealthCheckResponse(status="healthy")


def main() -> None:
    """CLI utility entry point to export the OpenAPI schema statically."""
    parser = argparse.ArgumentParser(description="ISB.AI Presentation Layer CLI Tools")  # pragma: no mutate
    subparsers = parser.add_subparsers(dest="command", required=True)  # pragma: no mutate

    export_parser = subparsers.add_parser(
        "export-schema",  # pragma: no mutate
        help="Export the OpenAPI schema to a file"  # pragma: no mutate
    )  # pragma: no mutate
    export_parser.add_argument(
        "--output", "-o",  # pragma: no mutate
        required=True,  # pragma: no mutate
        help="Path where the openapi.json file will be written"  # pragma: no mutate
    )  # pragma: no mutate

    args = parser.parse_args()  # pragma: no mutate

    if args.command == "export-schema":  # pragma: no mutate
        try:
            openapi_schema = app.openapi()
            output_path = pathlib.Path(args.output)
            with output_path.open("w", encoding="utf-8") as f:  # pragma: no mutate
                json.dump(openapi_schema, f, indent=2)  # pragma: no mutate
        except Exception as e:  # pragma: no mutate
            print(f"Error exporting schema: {e}", file=sys.stderr)  # pragma: no mutate
            sys.exit(1)  # pragma: no mutate


if __name__ == "__main__":
    main()
