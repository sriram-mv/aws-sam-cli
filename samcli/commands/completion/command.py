"""
CLI command for "completion" command
"""
from typing import Type

from click import Command, command

from samcli.cli.main import pass_context
from samcli.commands._utils.command_exception_handler import command_exception_handler
from samcli.commands.completion.command_context import COMMAND_NAME, CompletionCommandContext
from samcli.commands.completion.core.command import CompletionBaseCommand, CompletionSubCommand


def create_command() -> Type[Command]:
    """
    Factory method for creating a Completion command
    Returns
    -------
    Type[Command]
        Sub-command class if the command line args include
        sub-commands, otherwise returns the base command class
    """
    if CompletionCommandContext().sub_commands:
        return CompletionSubCommand
    return CompletionBaseCommand


@command(name=COMMAND_NAME, cls=create_command())
@pass_context
@command_exception_handler
def cli(ctx):
    """
    `sam completion` command entry point
    """
