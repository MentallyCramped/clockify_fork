import datetime as dt
import json
import pandas as pd
import pytz
import requests

from config import Config

BASE_API = "https://api.clockify.me/api/v1"
TIME_ENTRIES_ENDPOINT = "/workspaces/{workspaceId}/user/{userId}/time-entries"
PROJECTS_ENDPOINT = "/workspaces/{workspaceId}/projects"


class TimeEntriesApi(object):
    def __init__(self) -> None:

        self.headers = {"X-Api-Key": Config.api_key}
        self.time_api = BASE_API + TIME_ENTRIES_ENDPOINT.format(
            workspaceId=Config.workspace_id, userId=Config.user_id
        )

    def get_recent_entries(self) -> list:
        resp = requests.get(self.time_api, headers=self.headers)
        entries = json.loads(resp.text)
        return entries

    def get_projects(self) -> list:
        project_api = BASE_API + PROJECTS_ENDPOINT.format(
            workspaceId=Config.workspace_id
        )
        resp = requests.get(project_api, headers=self.headers)
        projects = json.loads(resp.text)
        return projects

    def get_todays_entries(self, entries: list) -> list:
        entries_today = []
        today = dt.datetime.now(pytz.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        window_start = today - dt.timedelta(hours=5, minutes=30)
        window_end = today.replace(hour=18, minute=30)

        for entry in entries:
            time_interval = entry["timeInterval"]
            if not time_interval["end"]:
                continue
            start = pd.to_datetime(time_interval["start"])
            end = pd.to_datetime(time_interval["end"])

            if start > window_start and end < window_end:
                entries_today.append(
                    dict(project_id=entry["projectId"], start=start, end=end)
                )
        return entries_today

    def get_projects_df(self, projects: list) -> pd.DataFrame:
        projects_list = []
        for project in projects:
            projects_list.append(dict(project_id=project["id"], name=project["name"]))
        projects_df = pd.DataFrame(projects_list)
        return projects_df

    def get_entries_df(self, entries: list) -> pd.DataFrame:
        entry_df = None
        if entries:
            entry_df = pd.DataFrame(entries)
        return entry_df
