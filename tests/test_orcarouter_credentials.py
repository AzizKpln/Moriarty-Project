"""Credential seam: two adapters, one durable result, exact-generation reauth."""

from __future__ import annotations

import json

import pytest

from moriarty.providers.orcarouter import (
    API_KEY_ADAPTER,
    PKCE_ADAPTER,
    MappingVault,
    OrcaConfigurationError,
    clear_credential,
    mark_reauthentication_required,
    needs_reauthentication,
    resolve_credential,
)

KEY_ONE = "sk-orca-" + "credential-one"
KEY_TWO = "sk-orca-" + "credential-two"


def test_api_key_adapter_saves_loads_and_clears() -> None:
    vault = MappingVault({})
    credential = API_KEY_ADAPTER.save(vault, KEY_ONE)

    assert credential.source == "api_key"
    assert credential.scope == "api"
    assert credential.generation == 1
    resolved = resolve_credential(vault)
    assert resolved is not None
    assert resolved.key == KEY_ONE
    assert resolved.source == "api_key"
    assert needs_reauthentication(vault) is False

    clear_credential(vault)
    assert resolve_credential(vault) is None
    assert vault.get("orcarouter_api_key") is None


def test_key_is_not_in_repr_or_public_surface() -> None:
    vault = MappingVault({})
    credential = API_KEY_ADAPTER.save(vault, KEY_ONE)
    assert KEY_ONE not in repr(credential)
    assert KEY_ONE not in json.dumps({k: v for k, v in vault._data.items() if k != "orcarouter_api_key"})


def test_api_key_adapter_rejects_bad_input() -> None:
    vault = MappingVault({})
    with pytest.raises(OrcaConfigurationError):
        API_KEY_ADAPTER.save(vault, "")
    with pytest.raises(OrcaConfigurationError):
        API_KEY_ADAPTER.save(vault, "not-an-orca-key")


def test_pkce_adapter_produces_the_same_credential_result() -> None:
    api_vault = MappingVault({})
    pkce_vault = MappingVault({})
    API_KEY_ADAPTER.save(api_vault, KEY_ONE)
    PKCE_ADAPTER.save(pkce_vault, KEY_TWO, account_id="user-9", scope="api")

    api_credential = resolve_credential(api_vault)
    pkce_credential = resolve_credential(pkce_vault)
    assert api_credential is not None and pkce_credential is not None
    assert type(api_credential) is type(pkce_credential)
    assert api_credential.key.startswith("sk-orca-")
    assert pkce_credential.key.startswith("sk-orca-")
    assert pkce_credential.source == "pkce"
    assert pkce_credential.account_id == "user-9"
    assert pkce_credential.scope == "api"


def test_generation_guard_ignores_a_late_failure_from_an_old_credential() -> None:
    vault = MappingVault({})
    old = API_KEY_ADAPTER.save(vault, KEY_ONE)
    new = PKCE_ADAPTER.save(vault, KEY_TWO, account_id="user-2", scope="api")
    assert new.generation == old.generation + 1

    assert mark_reauthentication_required(vault, old) is False
    assert needs_reauthentication(vault) is False

    assert mark_reauthentication_required(vault, new) is True
    assert needs_reauthentication(vault) is True


def test_successful_replacement_clears_needs_reauth() -> None:
    vault = MappingVault({})
    credential = API_KEY_ADAPTER.save(vault, KEY_ONE)
    mark_reauthentication_required(vault, credential)
    assert needs_reauthentication(vault) is True
    replacement = PKCE_ADAPTER.save(vault, KEY_TWO, account_id="user-3", scope="api")
    assert needs_reauthentication(vault) is False
    assert replacement.generation == credential.generation + 1
