import os


class Config(object):
    special_project_id = os.getenv("SPECIAL_PROJECT_ID")
    discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    api_key = os.getenv("API_KEY")
    workspace_id = os.getenv("WORKSPACE_ID")
    user_id = os.getenv("USER_ID")
    special_project_name = os.getenv("SPECIAL_PROJECT_NAME")
    user_name = os.getenv("USER_NAME")
