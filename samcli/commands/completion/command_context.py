import functools
import os
import sys
from typing import Callable, List

import click

from samcli.cli.main import common_options, print_cmdline_args
from samcli.commands.completion.exceptions import InvalidCompletionCommandException
from samcli.lib.completion.shell_completer import Completer
from samcli.lib.telemetry.metric import track_command

COMMAND_NAME = "completion"


class CompletionCommandContext:
    def get_complete_command_paths(self) -> List[str]:
        """
        Get a list of strings representing the fully qualified commands invokable by sam completion

        Returns
        -------
        List[str]
            A string list of commands including the base command
        """
        return [self.base_command + " " + command for command in self.all_commands]

    @property
    def command_callback(self) -> Callable[[str], None]:
        """
        Returns the callback function as a callable with the sub command string
        """
        impl = CommandImplementation(command=self.sub_command_string)
        return functools.partial(impl.run_command)

    @property
    def all_commands(self) -> List[str]:
        """
        Returns all the commands from the commands list in the completion config
        """
        return list(Completer(COMMAND_NAME).completions.keys())

    @property
    def sub_command_string(self) -> str:
        """
        Returns a string representation of the sub-commands
        """
        return " ".join(self.sub_commands)

    @property
    def sub_commands(self) -> List[str]:
        """
        Returns the filtered command line arguments after "sam completion"
        """
        return self._filter_arguments(sys.argv[2:])

    @property
    def base_command(self) -> str:
        """
        Returns a string representation of the base command (e.g "sam completion")

        click.get_current_context().command_path returns the entire command by the time it
        gets to the leaf node. We just want "sam completion" so we extract it from that string
        """
        return f"sam {COMMAND_NAME}"

    @staticmethod
    def _filter_arguments(commands: List[str]) -> List[str]:
        """
        Take a list of command line arguments and filter out all flags

        Parameters
        ----------
        commands: List[str]
            The command line arguments

        Returns
        -------
            List of strings after filtering it all flags

        """
        return list(filter(lambda arg: not arg.startswith("-"), commands))


class CommandImplementation:
    def __init__(self, command: str):
        """
        Constructor used for instantiating a command implementation object

        Parameters
        ----------
        command: str
            Name of the command that is being executed
        """
        self.command = command
        self.completion_command = CompletionCommandContext()

    @track_command
    @print_cmdline_args
    @common_options
    def run_command(self):
        """
        Run the necessary logic for the `sam completion` command

        Raises
        ------
        InvalidCompletionCommandException
        """
        if self.completion_command.sub_commands and self.command not in self.completion_command.all_commands:
            raise InvalidCompletionCommandException(
                f"Shell not found. Try using one of the following available shells:{os.linesep}"
                f"{os.linesep.join([command for command in self.completion_command.get_complete_command_paths()])}"
            )
        completer = Completer(command=self.command)
        click.secho(completer.open_completion())
