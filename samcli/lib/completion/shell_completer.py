"""
Library housing the logic for handling AWS SAM CLI completion.
"""
import logging


LOG = logging.getLogger(__name__)


class Completer:
    def __init__(self, command: str):
        """
        Constructor for instantiating a Documentation object
        Parameters
        ----------
        command: str
            String name of the command for which to find documentation
        """
        self.command = command
        self.completions = {
            "fish": "_SAM_COMPLETE=fish_source sam > ~/.config/fish/completions/sam.fish",
            "bash": "_SAM_COMPLETE=bash_source sam > ~/.sam-complete.bash && echo '. ~/.sam-complete.bash' >> ~/.bashrc && source ~/.bashrc",
            "zsh": "_SAM_COMPLETE=zsh_source sam > ~/.sam-complete.zsh && echo '. ~/.sam-complete.zsh' >> ~/.zshrc && source ~/.zshrc",
        }

    def open_completion(self):
        return self.completions.get(self.command, f"Valid shell arguments are: {' '.join(self.completions.keys())}")
