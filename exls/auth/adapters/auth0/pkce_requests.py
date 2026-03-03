"""PKCE request data models for Auth0 adapter."""

from pydantic import BaseModel, Field, StrictStr


class PkceCodeExchangeRequest(BaseModel):
    """Parameters for exchanging authorization code for tokens via Auth0."""

    client_id: StrictStr
    code: StrictStr
    code_verifier: StrictStr
    redirect_uri: StrictStr
    grant_type: StrictStr = Field(default="authorization_code")
    domain: StrictStr
