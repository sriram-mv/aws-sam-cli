"""
Module contains classes for creating the completion command from click
"""
import os
from typing import List, Optional

from click import Command, Context, MultiCommand, style

from samcli.cli.row_modifiers import RowDefinition
from samcli.commands.completion.command_context import COMMAND_NAME, CompletionCommandContext
from samcli.commands.completion.core.formatter import CompletionCommandHelpTextFormatter

HELP_TEXT = "NEW! Completion support for AWS SAM CLI"
DESCRIPTION = """
    Shell Completion support for AWS SAM CLI in bash, zsh and fish.
"""


class CompletionBaseCommand(Command):
    class CustomFormatterContext(Context):
        formatter_class = CompletionCommandHelpTextFormatter

    context_class = CustomFormatterContext

    def __init__(self, *args, **kwargs):
        """
        Constructor for instantiating a base command for the completion command
        """
        self.completion_command = CompletionCommandContext()
        command_callback = self.completion_command.command_callback
        super().__init__(name=COMMAND_NAME, help=HELP_TEXT, callback=command_callback)

    @staticmethod
    def format_description(formatter: CompletionCommandHelpTextFormatter):
        """
        Formats the description of the help text for the completion command.

        Parameters
        ----------
        formatter: CompletionCommandHelpTextFormatter
            A formatter instance to use for formatting the help text
        """
        with formatter.indented_section(name="Description", extra_indents=1):
            formatter.write_rd(
                [
                    RowDefinition(
                        text="",
                        name=DESCRIPTION
                    ),
                ],
            )

    @staticmethod
    def format_examples(formatter: CompletionCommandHelpTextFormatter):
        """
        Formats the description of the help text for the completion command.

        Parameters
        ----------
        formatter: CompletionCommandHelpTextFormatter
            A formatter instance to use for formatting the help text
        """
        with formatter.indented_section(name="Examples", extra_indents=1):
            formatter.write_rd(
                [
                    RowDefinition(
                        text="",
                        name=DESCRIPTION
                    ),
                ],
            )

    def format_sub_commands(self, formatter: CompletionCommandHelpTextFormatter):
        """
        Formats the sub-commands of the help text for the completion command.

        Parameters
        ----------
        formatter: CompletionCommandHelpTextFormatter
            A formatter instance to use for formatting the help text
        """
        with formatter.indented_section(name="Commands", extra_indents=1):
            formatter.write_rd(
                [
                    RowDefinition(self.completion_command.base_command + " " + command)
                    for command in self.completion_command.all_commands
                ],
                col_max=50,
            )

    def format_options(self, ctx: Context, formatter: CompletionCommandHelpTextFormatter):  # type:ignore
        """
        Overrides the format_options method from the parent class to update
        the help text formatting in a consistent method for the AWS SAM CLI

        Parameters
        ----------
        ctx: Context
            The click command context
        formatter: CompletionCommandHelpTextFormatter
            A formatter instance to use for formatting the help text
        """
        CompletionBaseCommand.format_description(formatter)
        self.format_sub_commands(formatter)


class CompletionSubCommand(MultiCommand):
    def __init__(self, command: Optional[List[str]] = None, *args, **kwargs):
        """
        Constructor for instantiating a sub-command for the completion command

        Parameters
        ----------
        command: Optional[List[str]]
            Optional list of strings representing the fully resolved command name (e.g. ["completion", "local", "invoke"])
        """
        super().__init__(*args, **kwargs)
        self.completion_command = CompletionCommandContext()
        self.command = command or self.completion_command.sub_commands
        self.command_string = self.completion_command.sub_command_string
        self.command_callback = self.completion_command.command_callback

    def get_command(self, ctx: Context, cmd_name: str) -> Command:
        """
        Overriding the get_command method from the parent class.

        This method recursively gets creates sub-commands until
        it reaches the leaf command, then it returns that as a click command.

        Parameters
        ----------
        ctx: Context
            The click command context
        cmd_name: str
            Name of the next command to be added as a sub-command or the leaf command

        Returns
        -------
        Command
            Returns either a sub-command to be recursively added to the command tree,
            or the leaf command to be invoked by the command handler

        """
        next_command = self.command.pop(0)
        if not self.command:
            return CompletionBaseCommand(
                name=next_command,
                short_help=f"Completion for {self.command_string}",
                callback=self.command_callback,
            )
        return CompletionSubCommand(command=self.command)

    def list_commands(self, ctx: Context) -> List[str]:
        """
        Overrides the list_command method from the parent class.
        Used for the Command class to understand all possible sub-commands.

        Parameters
        ----------
        ctx: Context
            The click command context

        Returns
        -------
        List[str]
            List of strings representing sub-commands callable by the completion command
        """
        return self.completion_command.all_commands
