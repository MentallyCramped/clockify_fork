from typing import Tuple

import pandas as pd
import requests

from config import Config
from report_api import ReportApi
from time_entries_api import TimeEntriesApi


class ProductivityUpdate:
    def __init__(self):
        self.report = ReportApi()

    def _get_daily_message(self) -> str:
        message = ""
        time_api = TimeEntriesApi()
        recent_entries = time_api.get_recent_entries()
        entries = time_api.get_todays_entries(recent_entries)
        if not entries:
            message += self._get_no_work_today_message()
        else:
            summary_df = self.generate_summary_df(entries)
            total_hours, total_minutes = self.get_total_time(summary_df)
            project_to_time_dict = self.get_special_project_time(summary_df)
            message += self._get_work_done_today_message(
                total_hours, total_minutes, project_to_time_dict
            )
        return message

    def _get_work_done_today_message(
        self, total_hours: int, total_minutes: int, project_to_time_dict : dict
    ) -> str:
        final_message = "🕰  Daily stats - Total time: {total_hours} hours and {total_minutes} minutes.\n"
        for project_name, time_details in project_to_time_dict.items():
            final_message += project_name + " ---> Time: {prep_hours} hours and {prep_minutes} minutes".format(
            prep_hours=time_details[0],
            prep_minutes=time_details[1]
            ) + "\n"
        return final_message

    def _get_no_work_today_message(self) -> str:
        return "🕰 {} did not work today".format(Config.user_name)

    def generate_message(self) -> str:
        message = "Updates for {}\n".format(Config.user_name)
        message += self._get_daily_message()
        weekly_message = ReportApi().report("weekly")
        message += "\n" + weekly_message
        return message

    def generate_summary_df(self, entries: list):
        time_api = TimeEntriesApi()
        projects = time_api.get_projects()
        entry_df = time_api.get_entries_df(entries)
        projects_df = time_api.get_projects_df(projects)
        entry_df["hours"] = entry_df["end"] - entry_df["start"]
        entry_df = entry_df.groupby("project_id").agg({"hours": sum}).reset_index()
        summary_df = pd.merge(entry_df, projects_df, on="project_id")
        return summary_df

    def get_total_time(self, summary_df: pd.DataFrame) -> Tuple[int, int]:
        total_time = summary_df["hours"].sum().seconds
        total_hours = total_time // (60 * 60)
        total_minutes = (total_time - total_hours * 60 * 60) // 60
        return total_hours, total_minutes

    def get_special_project_time(self, summary_df: pd.DataFrame):
        # if Config.special_project_name in summary_df["name"].tolist():
        project_to_hours_map = {}
        for project_row in summary_df.iterrows():
            print(project_row[1])
            prep_time = (
                project_row[1]["hours"].seconds
            )
            prep_hours = prep_time // (60 * 60)
            prep_minutes = (prep_time - prep_hours * 60 * 60) // 60
            if(prep_minutes > 0 or prep_hours > 0):
                project_to_hours_map[project_row[1]["name"]] = (prep_hours, prep_minutes)
        return project_to_hours_map

    def notify(self, message: str) -> int:
        message_dict = {"content": message}
        resp = requests.post(
            url=Config.discord_webhook_url,
            json=message_dict,
            headers={"Content-Type": "application/json"},
        )
        # print(message_dict)
        return 200

    def run(self):
        message = self.generate_message()
        return self.notify(message)


if __name__ == "__main__":
    p = ProductivityUpdate()
    p.run()
