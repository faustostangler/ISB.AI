import sys
from isb.config import settings


def main() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print(f"Booting Intelligent Second Brain (ISB.AI) Monolith")
    print(f"Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print("CRITICAL: Storage connection URLs must be configured.", file=sys.stderr)
        sys.exit(1)

    print("Platform adapters successfully initialized. Worker is ready.")


if __name__ == "__main__":
    main()
