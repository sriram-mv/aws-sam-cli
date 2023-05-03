from samcli.commands.exceptions import UserException


class InvalidCompletionCommandException(UserException):
    """
    Exception when the completion command fails
    """
