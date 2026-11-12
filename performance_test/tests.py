"""
Load test for Open VTB: GET on every list endpoint, no filters, with pageSize=100 and page=10.
"""

from performance_test.bencher import report_to_bencher
from performance_test.locust.utils import ListEndpointsTest, list_tasks

AUTH_TOKEN = "performance_token"
AUTH_HEADERS = {"Authorization": f"Token {AUTH_TOKEN}"}

report_to_bencher()


class OpenVTBEndpoints(ListEndpointsTest):
    headers = AUTH_HEADERS
    tasks = list_tasks(
        {
            "verzoeken_list": "/verzoeken/api/v1/verzoeken",
            "taken_list": "/taken/api/v1/externetaken",
            "berichten_list": "/berichten/api/v1/berichten",
        },
        params="pageSize=100&page=10",
    )
