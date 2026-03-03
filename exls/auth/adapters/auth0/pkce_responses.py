"""PKCE response data models from Auth0."""

from typing import Optional

from pydantic import BaseModel, StrictStr


class PkceTokenResponse(BaseModel):
    """Token response from Auth0 /oauth/token endpoint."""

    access_token: StrictStr
    id_token: StrictStr
    refresh_token: Optional[StrictStr] = None
    token_type: StrictStr
    expires_in: int
    scope: StrictStr
