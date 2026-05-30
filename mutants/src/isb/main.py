import sys
from collections.abc import Callable
from typing import Annotated, ClassVar

from isb.config import settings

MutantDict = Annotated[dict[str, Callable], "Mutant"] # type: ignore


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None): # type: ignore
    """Forward call to original or mutated function, depending on the environment"""
    import os  # type: ignore
    mutant_under_test = os.environ['MUTANT_UNDER_TEST'] # type: ignore
    if mutant_under_test == 'fail': # type: ignore
        from mutmut.__main__ import MutmutProgrammaticFailException  # type: ignore
        raise MutmutProgrammaticFailException('Failed programmatically')       # type: ignore
    elif mutant_under_test == 'stats': # type: ignore
        from mutmut.__main__ import record_trampoline_hit  # type: ignore
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


def main() -> None:
    args = []# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_main__mutmut_orig, x_main__mutmut_mutants, args, kwargs, None)


def x_main__mutmut_orig() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print("CRITICAL: Storage connection URLs must be configured.", file=sys.stderr)
        sys.exit(1)

    print("Platform adapters successfully initialized. Worker is ready.")


def x_main__mutmut_1() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print(None)
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print("CRITICAL: Storage connection URLs must be configured.", file=sys.stderr)
        sys.exit(1)

    print("Platform adapters successfully initialized. Worker is ready.")


def x_main__mutmut_2() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("XX--------------------------------------------------XX")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print("CRITICAL: Storage connection URLs must be configured.", file=sys.stderr)
        sys.exit(1)

    print("Platform adapters successfully initialized. Worker is ready.")


def x_main__mutmut_3() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print(None)
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print("CRITICAL: Storage connection URLs must be configured.", file=sys.stderr)
        sys.exit(1)

    print("Platform adapters successfully initialized. Worker is ready.")


def x_main__mutmut_4() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print(None)
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print("CRITICAL: Storage connection URLs must be configured.", file=sys.stderr)
        sys.exit(1)

    print("Platform adapters successfully initialized. Worker is ready.")


def x_main__mutmut_5() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(None)
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print("CRITICAL: Storage connection URLs must be configured.", file=sys.stderr)
        sys.exit(1)

    print("Platform adapters successfully initialized. Worker is ready.")


def x_main__mutmut_6() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(None)
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print("CRITICAL: Storage connection URLs must be configured.", file=sys.stderr)
        sys.exit(1)

    print("Platform adapters successfully initialized. Worker is ready.")


def x_main__mutmut_7() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print(None)

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print("CRITICAL: Storage connection URLs must be configured.", file=sys.stderr)
        sys.exit(1)

    print("Platform adapters successfully initialized. Worker is ready.")


def x_main__mutmut_8() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("XX--------------------------------------------------XX")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print("CRITICAL: Storage connection URLs must be configured.", file=sys.stderr)
        sys.exit(1)

    print("Platform adapters successfully initialized. Worker is ready.")


def x_main__mutmut_9() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL and not settings.REDIS_URL:
        print("CRITICAL: Storage connection URLs must be configured.", file=sys.stderr)
        sys.exit(1)

    print("Platform adapters successfully initialized. Worker is ready.")


def x_main__mutmut_10() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if settings.DATABASE_URL or not settings.REDIS_URL:
        print("CRITICAL: Storage connection URLs must be configured.", file=sys.stderr)
        sys.exit(1)

    print("Platform adapters successfully initialized. Worker is ready.")


def x_main__mutmut_11() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or settings.REDIS_URL:
        print("CRITICAL: Storage connection URLs must be configured.", file=sys.stderr)
        sys.exit(1)

    print("Platform adapters successfully initialized. Worker is ready.")


def x_main__mutmut_12() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print(None, file=sys.stderr)
        sys.exit(1)

    print("Platform adapters successfully initialized. Worker is ready.")


def x_main__mutmut_13() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print("CRITICAL: Storage connection URLs must be configured.", file=None)
        sys.exit(1)

    print("Platform adapters successfully initialized. Worker is ready.")


def x_main__mutmut_14() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print(file=sys.stderr)
        sys.exit(1)

    print("Platform adapters successfully initialized. Worker is ready.")


def x_main__mutmut_15() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print("CRITICAL: Storage connection URLs must be configured.", )
        sys.exit(1)

    print("Platform adapters successfully initialized. Worker is ready.")


def x_main__mutmut_16() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print("XXCRITICAL: Storage connection URLs must be configured.XX", file=sys.stderr)
        sys.exit(1)

    print("Platform adapters successfully initialized. Worker is ready.")


def x_main__mutmut_17() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print("critical: storage connection urls must be configured.", file=sys.stderr)
        sys.exit(1)

    print("Platform adapters successfully initialized. Worker is ready.")


def x_main__mutmut_18() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print("CRITICAL: STORAGE CONNECTION URLS MUST BE CONFIGURED.", file=sys.stderr)
        sys.exit(1)

    print("Platform adapters successfully initialized. Worker is ready.")


def x_main__mutmut_19() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print("CRITICAL: Storage connection URLs must be configured.", file=sys.stderr)
        sys.exit(None)

    print("Platform adapters successfully initialized. Worker is ready.")


def x_main__mutmut_20() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print("CRITICAL: Storage connection URLs must be configured.", file=sys.stderr)
        sys.exit(2)

    print("Platform adapters successfully initialized. Worker is ready.")


def x_main__mutmut_21() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print("CRITICAL: Storage connection URLs must be configured.", file=sys.stderr)
        sys.exit(1)

    print(None)


def x_main__mutmut_22() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print("CRITICAL: Storage connection URLs must be configured.", file=sys.stderr)
        sys.exit(1)

    print("XXPlatform adapters successfully initialized. Worker is ready.XX")


def x_main__mutmut_23() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print("CRITICAL: Storage connection URLs must be configured.", file=sys.stderr)
        sys.exit(1)

    print("platform adapters successfully initialized. worker is ready.")


def x_main__mutmut_24() -> None:
    """The Composition Root and entry point for CLI and background worker roles.

    This function initializes infrastructure configurations and wires adapters
    to ports before starting worker execution loops.
    """
    print("--------------------------------------------------")
    print("Booting Intelligent Second Brain (ISB.AI) Monolith")
    print("Role: Worker/CLI")
    print(f"Environment: {settings.ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("--------------------------------------------------")

    # In a fully realized Monolith, we would wire our adapters and resolve dependency graphs.
    # For this skeleton, we perform validation checks and print readiness.
    if not settings.DATABASE_URL or not settings.REDIS_URL:
        print("CRITICAL: Storage connection URLs must be configured.", file=sys.stderr)
        sys.exit(1)

    print("PLATFORM ADAPTERS SUCCESSFULLY INITIALIZED. WORKER IS READY.")

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
    'x_main__mutmut_16': x_main__mutmut_16,
    'x_main__mutmut_17': x_main__mutmut_17,
    'x_main__mutmut_18': x_main__mutmut_18,
    'x_main__mutmut_19': x_main__mutmut_19,
    'x_main__mutmut_20': x_main__mutmut_20,
    'x_main__mutmut_21': x_main__mutmut_21,
    'x_main__mutmut_22': x_main__mutmut_22,
    'x_main__mutmut_23': x_main__mutmut_23,
    'x_main__mutmut_24': x_main__mutmut_24
}
x_main__mutmut_orig.__name__ = 'x_main'


if __name__ == "__main__":
    main()
