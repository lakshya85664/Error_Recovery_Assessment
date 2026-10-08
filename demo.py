import logging

from src.error_recovery import recover, FatalError


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
)


def show_result(label, city, cache):
    print()
    print("=" * 60)
    print(label)
    print("=" * 60)

    try:
        result = recover(city, cache)
        print("Result:", result)

    except FatalError as error:
        print("FatalError propagated:", error)


show_result(
    "1. Primary success",
    "Pune",
    {},
)

show_result(
    "2. Transient failure -> backup",
    "Rivertown",
    {},
)

show_result(
    "3. Not found -> cache",
    "Atlantis",
    {"Atlantis": 15.0},
)

show_result(
    "4. Not found -> no value",
    "Atlantis",
    {},
)

show_result(
    "5. Fatal error -> propagate",
    "Brokenville",
    {},
)