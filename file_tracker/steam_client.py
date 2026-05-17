"""Steam authentication and app info retrieval."""
from base64 import b64decode
from time import sleep

import steam.guard
from gevent.timeout import Timeout as GeventTimeout
from steam.client import SteamClient

APP_ID = 730
DEPOT_ID = 2347770
PRODUCT_INFO_TIMEOUT_SECONDS = 60
PRODUCT_INFO_MAX_ATTEMPTS = 3
PRODUCT_INFO_RETRY_DELAY_SECONDS = 5


def login(username: str, password: str, shared_secret: str | None = None) -> SteamClient:
    client = SteamClient()

    if shared_secret:
        two_factor_code = steam.guard.generate_twofactor_code(b64decode(shared_secret))
        client.login(username, password, two_factor_code=two_factor_code)
    else:
        client.login(username, password)

    return client


def anonymous_login() -> SteamClient:
    client = SteamClient()
    client.anonymous_login()
    return client


def _safe_logout(client: SteamClient) -> None:
    # The connection may already be dead after a timeout; logging out is
    # best-effort cleanup so a fresh client can reconnect cleanly.
    try:
        client.logout()
    except Exception:
        pass


def _fetch_manifest_id(client: SteamClient) -> str:
    info = client.get_product_info(apps=[APP_ID], timeout=PRODUCT_INFO_TIMEOUT_SECONDS)
    depots = info["apps"][APP_ID]["depots"]
    manifest_id = depots[str(DEPOT_ID)]["manifests"]["public"]["gid"]
    return str(manifest_id)


def get_latest_manifest_id() -> str:
    """Read the public CS2 manifest GID using a fresh anonymous client.

    App 730 product info is public, so no account credentials are needed.
    The CM connection is re-established before every retry: a dropped
    connection times out identically forever, so reusing the same client
    makes retries pointless.
    """
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
