class UnravelError(Exception):
    """Base class for all unravel errors."""


class UndefinedChunkError(UnravelError):
    def __init__(self, name: str, referenced_from: str, defined_at: str) -> None:
        self.name = name
        self.referenced_from = referenced_from
        self.defined_at = defined_at
        super().__init__(
            f'Undefined chunk "{name}"\n\n'
            f'Referenced from chunk "{referenced_from}"\n'
            f"defined at {defined_at}"
        )


class CircularReferenceError(UnravelError):
    def __init__(self, cycle: list[str]) -> None:
        path = " -> ".join(cycle)
        super().__init__(f"Circular reference: {path}")


class MalformedChunkError(UnravelError):
    pass
