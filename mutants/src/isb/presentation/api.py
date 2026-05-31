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
from typing import Annotated
from typing import Callable
from typing import ClassVar

MutantDict = Annotated[dict[str, Callable], "Mutant"] # type: ignore


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None): # type: ignore
    """Forward call to original or mutated function, depending on the environment"""
    import os # type: ignore
    mutant_under_test = os.environ['MUTANT_UNDER_TEST'] # type: ignore
    if mutant_under_test == 'fail': # type: ignore
        from mutmut.__main__ import MutmutProgrammaticFailException # type: ignore
        raise MutmutProgrammaticFailException('Failed programmatically')       # type: ignore
    elif mutant_under_test == 'stats': # type: ignore
        from mutmut.__main__ import record_trampoline_hit # type: ignore
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__) # type: ignore
        # (for class methods, orig is bound and thus does not need the explicit self argument)
        result = orig(*call_args, **call_kwargs) # type: ignore
        return result # type: ignore
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_' # type: ignore
    if not mutant_under_test.startswith(prefix): # type: ignore
        result = orig(*call_args, **call_kwargs) # type: ignore
        return result # type: ignore
    mutant_name = mutant_under_test.rpartition('.')[-1] # type: ignore
    if self_arg is not None: # type: ignore
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs) # type: ignore
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs) # type: ignore
    return result # type: ignore


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
    args = []# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_main__mutmut_orig, x_main__mutmut_mutants, args, kwargs, None)


def x_main__mutmut_orig() -> None:
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


def x_main__mutmut_1() -> None:
    """CLI utility entry point to export the OpenAPI schema statically."""
    parser = argparse.ArgumentParser(description="ISB.AI Presentation Layer CLI Tools")  # pragma: no mutate
    subparsers = parser.add_subparsers(dest="command", required=True)  # pragma: no mutate

    export_parser = None  # pragma: no mutate
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


def x_main__mutmut_2() -> None:
    """CLI utility entry point to export the OpenAPI schema statically."""
    parser = argparse.ArgumentParser(description="ISB.AI Presentation Layer CLI Tools")  # pragma: no mutate
    subparsers = parser.add_subparsers(dest="command", required=True)  # pragma: no mutate

    export_parser = subparsers.add_parser(
        None,  # pragma: no mutate
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


def x_main__mutmut_3() -> None:
    """CLI utility entry point to export the OpenAPI schema statically."""
    parser = argparse.ArgumentParser(description="ISB.AI Presentation Layer CLI Tools")  # pragma: no mutate
    subparsers = parser.add_subparsers(dest="command", required=True)  # pragma: no mutate

    export_parser = subparsers.add_parser(
        "export-schema",  # pragma: no mutate
        help=None  # pragma: no mutate
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


def x_main__mutmut_4() -> None:
    """CLI utility entry point to export the OpenAPI schema statically."""
    parser = argparse.ArgumentParser(description="ISB.AI Presentation Layer CLI Tools")  # pragma: no mutate
    subparsers = parser.add_subparsers(dest="command", required=True)  # pragma: no mutate

    export_parser = subparsers.add_parser(
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


def x_main__mutmut_5() -> None:
    """CLI utility entry point to export the OpenAPI schema statically."""
    parser = argparse.ArgumentParser(description="ISB.AI Presentation Layer CLI Tools")  # pragma: no mutate
    subparsers = parser.add_subparsers(dest="command", required=True)  # pragma: no mutate

    export_parser = subparsers.add_parser(
        "export-schema",  # pragma: no mutate
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


def x_main__mutmut_6() -> None:
    """CLI utility entry point to export the OpenAPI schema statically."""
    parser = argparse.ArgumentParser(description="ISB.AI Presentation Layer CLI Tools")  # pragma: no mutate
    subparsers = parser.add_subparsers(dest="command", required=True)  # pragma: no mutate

    export_parser = subparsers.add_parser(
        "export-schema",  # pragma: no mutate
        help="Export the OpenAPI schema to a file"  # pragma: no mutate
    )  # pragma: no mutate
    export_parser.add_argument(
        None, "-o",  # pragma: no mutate
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


def x_main__mutmut_7() -> None:
    """CLI utility entry point to export the OpenAPI schema statically."""
    parser = argparse.ArgumentParser(description="ISB.AI Presentation Layer CLI Tools")  # pragma: no mutate
    subparsers = parser.add_subparsers(dest="command", required=True)  # pragma: no mutate

    export_parser = subparsers.add_parser(
        "export-schema",  # pragma: no mutate
        help="Export the OpenAPI schema to a file"  # pragma: no mutate
    )  # pragma: no mutate
    export_parser.add_argument(
        "--output", None,  # pragma: no mutate
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


def x_main__mutmut_8() -> None:
    """CLI utility entry point to export the OpenAPI schema statically."""
    parser = argparse.ArgumentParser(description="ISB.AI Presentation Layer CLI Tools")  # pragma: no mutate
    subparsers = parser.add_subparsers(dest="command", required=True)  # pragma: no mutate

    export_parser = subparsers.add_parser(
        "export-schema",  # pragma: no mutate
        help="Export the OpenAPI schema to a file"  # pragma: no mutate
    )  # pragma: no mutate
    export_parser.add_argument(
        "--output", "-o",  # pragma: no mutate
        required=None,  # pragma: no mutate
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


def x_main__mutmut_9() -> None:
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
        help=None  # pragma: no mutate
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


def x_main__mutmut_10() -> None:
    """CLI utility entry point to export the OpenAPI schema statically."""
    parser = argparse.ArgumentParser(description="ISB.AI Presentation Layer CLI Tools")  # pragma: no mutate
    subparsers = parser.add_subparsers(dest="command", required=True)  # pragma: no mutate

    export_parser = subparsers.add_parser(
        "export-schema",  # pragma: no mutate
        help="Export the OpenAPI schema to a file"  # pragma: no mutate
    )  # pragma: no mutate
    export_parser.add_argument(
        "-o",  # pragma: no mutate
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


def x_main__mutmut_11() -> None:
    """CLI utility entry point to export the OpenAPI schema statically."""
    parser = argparse.ArgumentParser(description="ISB.AI Presentation Layer CLI Tools")  # pragma: no mutate
    subparsers = parser.add_subparsers(dest="command", required=True)  # pragma: no mutate

    export_parser = subparsers.add_parser(
        "export-schema",  # pragma: no mutate
        help="Export the OpenAPI schema to a file"  # pragma: no mutate
    )  # pragma: no mutate
    export_parser.add_argument(
        "--output", required=True,  # pragma: no mutate
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


def x_main__mutmut_12() -> None:
    """CLI utility entry point to export the OpenAPI schema statically."""
    parser = argparse.ArgumentParser(description="ISB.AI Presentation Layer CLI Tools")  # pragma: no mutate
    subparsers = parser.add_subparsers(dest="command", required=True)  # pragma: no mutate

    export_parser = subparsers.add_parser(
        "export-schema",  # pragma: no mutate
        help="Export the OpenAPI schema to a file"  # pragma: no mutate
    )  # pragma: no mutate
    export_parser.add_argument(
        "--output", "-o",  # pragma: no mutate
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


def x_main__mutmut_13() -> None:
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


def x_main__mutmut_14() -> None:
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
            openapi_schema = None
            output_path = pathlib.Path(args.output)
            with output_path.open("w", encoding="utf-8") as f:  # pragma: no mutate
                json.dump(openapi_schema, f, indent=2)  # pragma: no mutate
        except Exception as e:  # pragma: no mutate
            print(f"Error exporting schema: {e}", file=sys.stderr)  # pragma: no mutate
            sys.exit(1)  # pragma: no mutate


def x_main__mutmut_15() -> None:
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
            output_path = None
            with output_path.open("w", encoding="utf-8") as f:  # pragma: no mutate
                json.dump(openapi_schema, f, indent=2)  # pragma: no mutate
        except Exception as e:  # pragma: no mutate
            print(f"Error exporting schema: {e}", file=sys.stderr)  # pragma: no mutate
            sys.exit(1)  # pragma: no mutate


def x_main__mutmut_16() -> None:
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
            output_path = pathlib.Path(None)
            with output_path.open("w", encoding="utf-8") as f:  # pragma: no mutate
                json.dump(openapi_schema, f, indent=2)  # pragma: no mutate
        except Exception as e:  # pragma: no mutate
            print(f"Error exporting schema: {e}", file=sys.stderr)  # pragma: no mutate
            sys.exit(1)  # pragma: no mutate

x_main__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_main__mutmut_1': x_main__mutmut_1, 
    'x_main__mutmut_2': x_main__mutmut_2, 
    'x_main__mutmut_3': x_main__mutmut_3, 
    'x_main__mutmut_4': x_main__mutmut_4, 
    'x_main__mutmut_5': x_main__mutmut_5, 
    'x_main__mutmut_6': x_main__mutmut_6, 
    'x_main__mutmut_7': x_main__mutmut_7, 
    'x_main__mutmut_8': x_main__mutmut_8, 
    'x_main__mutmut_9': x_main__mutmut_9, 
    'x_main__mutmut_10': x_main__mutmut_10, 
    'x_main__mutmut_11': x_main__mutmut_11, 
    'x_main__mutmut_12': x_main__mutmut_12, 
    'x_main__mutmut_13': x_main__mutmut_13, 
    'x_main__mutmut_14': x_main__mutmut_14, 
    'x_main__mutmut_15': x_main__mutmut_15, 
    'x_main__mutmut_16': x_main__mutmut_16
}
x_main__mutmut_orig.__name__ = 'x_main'


if __name__ == "__main__":
    main()
