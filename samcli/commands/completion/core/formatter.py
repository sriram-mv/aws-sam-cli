"""
Base formatter for the completion command help text
"""
from samcli.cli.formatters import RootCommandHelpTextFormatter
from samcli.cli.row_modifiers import BaseLineRowModifier


class CompletionCommandHelpTextFormatter(RootCommandHelpTextFormatter):
    def __init__(self, *args, **kwargs):
        """
        Constructor for instantiating a formatter object used for formatting help text
        """
        super().__init__(*args, **kwargs)
        self.left_justification_length = self.width // 2 - self.indent_increment
        self.modifiers = [BaseLineRowModifier()]
