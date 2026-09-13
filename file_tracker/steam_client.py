"""Steam authentication and app info retrieval."""
import logging
from base64 import b64decode
from time import sleep

import steam.guard
from gevent.timeout import Timeout as GeventTimeout
from steam.client import SteamClient
from steam.enums import EResult
from steam.webauth import WebAuth

logger = logging.getLogger(__name__)

APP_ID = 730
DEPOT_ID = 2347770
PRODUCT_INFO_TIMEOUT_SECONDS = 60
PRODUCT_INFO_MAX_ATTEMPTS = 3
PRODUCT_INFO_RETRY_DELAY_SECONDS = 5


class SteamLoginError(RuntimeError):
    """Raised when the authenticated Steam logon is rejected."""

    def __init__(self, result: EResult):
        self.result = result
        super().__init__(f"Steam login failed: {result.name} ({result.value})")


def login(username: str, password: str, shared_secret: str | None = None) -> SteamClient:
    """Log into Steam with the token-based flow."""
    two_factor_code = None
    if shared_secret:
        two_factor_code = steam.guard.generate_twofactor_code(b64decode(shared_secret))

    web = WebAuth(username, password)
    web.login(code=two_factor_code)

    client = SteamClient()
    result = client.login(username, access_token=web.refresh_token)

    if result != EResult.OK:
        raise SteamLoginError(EResult(result))

    return client


def anonymous_login() -> SteamClient:
    client = SteamClient()
    client.anonymous_login()
    return client


def _safe_logout(client: SteamClient) -> None:
    try:
        client.logout()
    except Exception:
        logger.warning("Failed to log out of Steam", exc_info=True)


def _fetch_manifest_id(client: SteamClient) -> str:
    info = client.get_product_info(
        apps=[APP_ID],
        timeout=PRODUCT_INFO_TIMEOUT_SECONDS,
        auto_access_tokens=False,
    )
    depots = info["apps"][APP_ID]["depots"]
    manifest_id = depots[str(DEPOT_ID)]["manifests"]["public"]["gid"]
    return str(manifest_id)


def get_latest_manifest_id() -> str:
    """Read the public CS2 manifest GID using a fresh anonymous client."""
    last_error: GeventTimeout | None = None
    client = anonymous_login()

    try:
        for attempt in range(1, PRODUCT_INFO_MAX_ATTEMPTS + 1):
            try:
                return _fetch_manifest_id(client)
            except GeventTimeout as exc:
                last_error = exc
                if attempt == PRODUCT_INFO_MAX_ATTEMPTS:
                    break

                print(
                    "Timed out fetching Steam product info "
                    f"(attempt {attempt}/{PRODUCT_INFO_MAX_ATTEMPTS}), reconnecting..."
                )
                _safe_logout(client)
                sleep(PRODUCT_INFO_RETRY_DELAY_SECONDS)
                client = anonymous_login()
    finally:
        _safe_logout(client)

    raise RuntimeError(
        "Failed to fetch Steam product info after repeated timeouts"
    ) from last_error
