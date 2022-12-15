from PyInstaller.utils import hooks
from installer.pyinstaller.hidden_imports import SAM_CLI_HIDDEN_IMPORTS

hiddenimports = SAM_CLI_HIDDEN_IMPORTS

datas = (
    hooks.collect_all(
        "samcli", include_py_files=True, include_datas=["hook_packages/terraform/copy_terraform_built_artifacts.py"]
    )[0]
    + hooks.collect_data_files("samcli")
    + hooks.collect_data_files("samtranslator")
    + hooks.collect_data_files("aws_lambda_builders")
    + hooks.collect_all("pbr", include_py_files=True)[0]
    + hooks.collect_all("cfnlint", include_py_files=True)[0]
    + hooks.collect_all("jschema_to_python", include_py_files=True)[0]
    + hooks.collect_data_files("text_unidecode")
)
