# This is not the exact right place for this command since it depends on
# jwt and not the auth0 specific logic. But its fine for now.
from typing import Generic, Type, TypeVar

import jwt
from pydantic import BaseModel

from exls.shared.adapters.deserializer import DeserializationError, PydanticDeserializer
from exls.shared.core.ports.command import BaseCommand, CommandError

T = TypeVar("T", bound=BaseModel)


class JWTCommandError(CommandError):
    pass


class DecodeTokenMetadataCommand(Generic[T], BaseCommand[T]):
    def __init__(self, token: str, model: Type[T]):
        self.token: str = token
        self.model: Type[T] = model
        self.deserializer: PydanticDeserializer[T] = PydanticDeserializer()

    def execute(self) -> T:
        try:
            decoded_token = jwt.decode(self.token, options={"verify_signature": False})
            return self.deserializer.deserialize(decoded_token, self.model)
        except DeserializationError as e:
            raise JWTCommandError(
                message=f"error while deserializing decoded token: {e}",
            ) from e
        except Exception as e:
            raise JWTCommandError(
                message=f"unexpected error while decoding token: {e}",
            ) from e
