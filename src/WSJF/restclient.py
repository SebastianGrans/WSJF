"""A minimal client for the WATS REST API.

The only ability of this client is to upload a report.
"""

import logging
import os
from urllib import parse

import requests
from requests.adapters import HTTPAdapter, Retry

from WSJF.models import WATSReport

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

DEFAULT_REST_API_TOKEN_ENV_NAME = "WATS_REST_API_TOKEN"  # noqa: S105 # This is not a hardcoded secret.


class WATSREST:
    """A minimal client for the WATS REST API."""

    def __init__(
        self,
        base_url: str,
        token_environment_variable: str = DEFAULT_REST_API_TOKEN_ENV_NAME,
    ):
        """A minimal client for the WATS REST API.

        * `base_url`: The URL to your WATS server. E.g.: `https://company.wats.com`
        * `token_environment_variable`: The name of the environment variable that contains the API token.

        """
        self.base_url = base_url
        self.url = f"{base_url}/api/"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        authorization_token = os.environ.get(token_environment_variable)
        if not authorization_token:
            errmsg = f"Environment variable {token_environment_variable} not set. Please set it to your WATS API token."
            raise ValueError(errmsg)
        self.headers["Authorization"] = f"Basic {authorization_token}"

        url_parse = parse.urlparse(base_url)
        scheme = url_parse.scheme

        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=2)
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount(scheme, adapter)

    def _post_request(self, payload: str, url_extension: str) -> requests.Response:
        url = self.url + url_extension
        response = self.session.post(url, data=payload, headers=self.headers, timeout=10)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            log.exception(f"Failed to make POST request. {response.text}")
            raise e

        return response

    def upload_report(self, report: WATSReport) -> requests.Response:
        """Uploads the report to the server."""
        url_extension = "Report/WSJF"
        response = self._post_request(report.model_dump_json(exclude_none=True), url_extension)
        response_json = response.json()
        log.info(f"{self.base_url}/Modules/ViewUUT_Report.html?id={response_json[0]['ID']}")
        return response
