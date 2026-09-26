class UnravelError(Exception):
    """Base class for all unravel errors."""


class UndefinedChunkError(UnravelError):
    def __init__(
        self,
        name: str,
        referenced_from: str,
        location: str,
        chain: list[str] | None = None,
    ) -> None:
        self.name = name
        self.referenced_from = referenced_from
        self.defined_at = location
        chain_text = f'\nReference chain: {" -> ".join(chain)}' if chain else ""
        super().__init__(
            f'{location}: undefined chunk "{name}" referenced from '
            f'chunk "{referenced_from}"{chain_text}'
        )


class CircularReferenceError(UnravelError):
    def __init__(self, cycle: list[str], locations: list[str] | None = None) -> None:
        detail = " -> ".join(cycle)
        if locations:
            detail += "\nReference sites: " + " -> ".join(locations)
        super().__init__(f"Circular reference: {detail}")


class MalformedChunkError(UnravelError):
    pass


class UnsafePathError(UnravelError):
    pass


class OwnershipError(UnravelError):
    pass


class ManifestError(UnravelError):
    pass


class CheckError(UnravelError):
    pass
