from typing import Protocol, Type, TypeVar

T_SerInput_Contra = TypeVar("T_SerInput_Contra", contravariant=True)
T_SerOutput = TypeVar("T_SerOutput")


class BaseDeserializer(Protocol[T_SerInput_Contra, T_SerOutput]):
    """Base deserializer for input and output types."""

    def deserialize(
        self, raw_data: T_SerInput_Contra, model: Type[T_SerOutput]
    ) -> T_SerOutput: ...
