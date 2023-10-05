# team_schedules

The example below shows how your app can help a manager track the weekly schedule of their team using the Nylas Calendar. It also provides more context and insight into upcoming meetings with external clients using the Nylas Contacts API.

For context, you can check the blog post ["Help Users Streamline Scheduling With The Nylas Calendar API"](https://www.nylas.com/blog/manage-team-schedules-nylas-calendar-api/).

## Setup

### System dependencies

- Python v3.x

### Gather environment variables

You'll need the following values:

```text
CLIENT_ID = ""
CLIENT_SECRET = ""
ACCESS_TOKEN = ""
```

Add the above values to a new `.env` file:

```bash
$ touch .env # Then add your env variables
```

Run the file **Team_Schedules.py**:

```bash
$ python3 Team_Schedules.py
```

## Learn more

Visit our [Nylas Python SDK documentation](https://developer.nylas.com/docs/developer-tools/sdk/python-sdk/) to learn more.
