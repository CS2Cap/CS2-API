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


def get_latest_manifest_id(client: SteamClient) -> str:
    last_error: GeventTimeout | None = None

    for attempt in range(1, PRODUCT_INFO_MAX_ATTEMPTS + 1):
        try:
            info = client.get_product_info(
                apps=[APP_ID],
                timeout=PRODUCT_INFO_TIMEOUT_SECONDS,
            )
            depots = info["apps"][APP_ID]["depots"]
            manifest_id = depots[str(DEPOT_ID)]["manifests"]["public"]["gid"]
            return str(manifest_id)
        except GeventTimeout as exc:
            last_error = exc
            if attempt == PRODUCT_INFO_MAX_ATTEMPTS:
                break

            print(
                "Timed out fetching Steam product info "
                f"(attempt {attempt}/{PRODUCT_INFO_MAX_ATTEMPTS}), retrying..."
            )
            sleep(PRODUCT_INFO_RETRY_DELAY_SECONDS)

    raise RuntimeError(
        "Failed to fetch Steam product info after repeated timeouts"
    ) from last_error
