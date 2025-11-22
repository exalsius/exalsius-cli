from exls.shared.core.ports.command import CommandError


class Auth0CommandError(CommandError):
    pass


class Auth0AuthentificationFailed(Auth0CommandError):
    pass


class Auth0TimeoutError(Auth0CommandError):
    pass


class Auth0TokenError(Auth0CommandError):
    pass


class Auth0AccessDeniedError(Auth0CommandError):
    pass


class KeyringCommandError(CommandError):
    pass
