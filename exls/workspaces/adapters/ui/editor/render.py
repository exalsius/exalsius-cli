from typing import Dict

from exls.workspaces.adapters.ui.configurators import IntegratedWorkspaceTemplates

# TODO: Add comments for each key in the dictionary
_DEFAULT_JUPYTER_WORKSPACE_TEMPLATE_EDITING_COMMENTS: Dict[str, str] = {
    "global": "Jupyter Notebook Helm Chart Values",
    "global.deploymentName": "The namem of your workspace deployment",
}

_DEFAULT_MARIMO_WORKSPACE_TEMPLATE_EDITING_COMMENTS: Dict[str, str] = {
    "global": "Marimo Helm Chart Values",
    "global.deploymentName": "The namem of your workspace deployment",
}

_DEFAULT_VSCODE_DEV_POD_WORKSPACE_TEMPLATE_EDITING_COMMENTS: Dict[str, str] = {
    "global": "VSCode Dev Pod Helm Chart Values",
    "global.deploymentName": "The namem of your workspace deployment",
}

_DEFAULT_DIST_TRAINING_WORKSPACE_TEMPLATE_EDITING_COMMENTS: Dict[str, str] = {
    "global": "Distributed Training Helm Chart Values",
    "global.deploymentName": "The namem of your workspace deployment",
}


_DEFAULT_WORKSPACE_TEMPLATE_EDITING_COMMENTS_MAP: Dict[
    IntegratedWorkspaceTemplates, Dict[str, str]
] = {
    IntegratedWorkspaceTemplates.JUPYTER: _DEFAULT_JUPYTER_WORKSPACE_TEMPLATE_EDITING_COMMENTS,
    IntegratedWorkspaceTemplates.MARIMO: _DEFAULT_MARIMO_WORKSPACE_TEMPLATE_EDITING_COMMENTS,
    IntegratedWorkspaceTemplates.DEV_POD: _DEFAULT_VSCODE_DEV_POD_WORKSPACE_TEMPLATE_EDITING_COMMENTS,
    IntegratedWorkspaceTemplates.DIST_TRAINING: _DEFAULT_DIST_TRAINING_WORKSPACE_TEMPLATE_EDITING_COMMENTS,
}


def get_workspace_template_editing_comments(
    template: IntegratedWorkspaceTemplates,
) -> Dict[str, str]:
    return _DEFAULT_WORKSPACE_TEMPLATE_EDITING_COMMENTS_MAP.get(template, {})
