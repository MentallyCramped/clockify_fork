import datetime as dt
import json
import logging
import os
from config import Config
from typing import Dict, Tuple

import requests

BASE_API = "https://reports.api.clockify.me/v1"

logger = logging.getLogger("clockify_reports_api")


class ReportApi(object):
    def __init__(self) -> None:
        api_key = os.getenv("API_KEY")
        self.workspace_id = os.getenv("WORKSPACE_ID")
        self.allowed_types = ["weekly"]
        self.headers = {"X-Api-Key": api_key}
        self.api_endpoint = (
            BASE_API
            + "/workspaces/{workspaceId}/reports/summary".format(
                workspaceId=self.workspace_id
            )
        )

    def report(self, type_: str):
        if type_ not in self.allowed_types:
            return
        if type_ == "weekly":
            api_response = self._get_weekly_report()

        total_time, prep_time = self._extract_time_values(api_response=api_response)

        report = "⏱  Weekly stats - Total time: {total_time} Prep Time: {prep_time}".format(
            total_time=self._format_seconds(total_time),
            prep_time=self._format_seconds(prep_time),
        )
        return report

    def _get_weekly_report(self):
        url = BASE_API + "/workspaces/{workspaceId}/reports/weekly".format(
            workspaceId=self.workspace_id
        )
        utc_now = dt.datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        days_since_week_start = utc_now.weekday()
        request_json = {
            "dateRangeStart": (
                utc_now - dt.timedelta(days=days_since_week_start)
            ).isoformat(),
            "dateRangeEnd": (
                utc_now + dt.timedelta(days=7 - days_since_week_start)
            ).isoformat(),
            "weeklyFilter": {"group": "PROJECT", "subgroup": "TIME"},
        }
        resp = requests.post(url=url, headers=self.headers, json=request_json)
        logger.info("Response code: %s" % resp.status_code)
        return json.loads(resp.text)

    def _extract_time_values(
        self, api_response: Dict, type_: str = None
    ) -> Tuple[int, int]:
        total_time = api_response["totals"][0]["totalTime"]
        prep_time = 0
        projects = api_response["groupOne"]
        for project in projects:
            if project["_id"] == Config.special_project_id:
                prep_time = project["duration"]
        return total_time, prep_time

    def _format_seconds(self, seconds: int):
        hours = seconds // (60 * 60)
        minutes = (seconds - hours * 60 * 60) // 60
        return "{hours} hours {minutes} minutes".format(hours=hours, minutes=minutes)


if __name__ == "__main__":
    c = ReportApi()
    print(c.report("weekly"))
