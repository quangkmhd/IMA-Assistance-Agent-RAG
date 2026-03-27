from __future__ import annotations


class ACLViolation(Exception):
    pass


class ACLGuard:
    def __init__(self, allowed_workspaces: set[str]) -> None:
        self._allowed_workspaces = allowed_workspaces

    def enforce(self, workspace_id: str) -> None:
        if workspace_id not in self._allowed_workspaces:
            raise ACLViolation(f"workspace_access_denied:{workspace_id}")
