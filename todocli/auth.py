import json
from oauth import get_oauth_session

todo_api_url = "https://graph.microsoft.com/beta/me/todo/"
calendar_api_url = "https://graph.microsoft.com/beta/me"


def parse_contents(response):
    return json.loads(response.content.decode())["value"]


# To Do data
def list_tasklists():
    to_do = get_oauth_session()
    t = to_do.get("{}/lists".format(todo_api_url))
    return parse_contents(t)

def list_tasks(tasklist_id):
    to_do = get_oauth_session()
    t = to_do.get("{}/lists/{}/tasks".format(todo_api_url, tasklist_id))
    nextLink = json.loads(t.content.decode()).get("@odata.nextLink", "")
    parsed_t = parse_contents(t)
    while nextLink != "":
        n = to_do.get(nextLink)
        nextLink = json.loads(n.content.decode()).get("@odata.nextLink", "")
        parsed_n = parse_contents(n)
        parsed_t.extend(parsed_n)
    return parsed_t


# Calendar data
def list_calendars():
    calendar = get_oauth_session()
    c = calendar.get("{}/calendars".format(calendar_api_url))
    return parse_contents(c)

def list_events(calendar_id):
    calendar = get_oauth_session()
    c = calendar.get("{}/calendars/{}/events".format(calendar_api_url, calendar_id))
    nextLink = json.loads(c.content.decode()).get("@odata.nextLink", "")
    parsed_c = parse_contents(c)
    while nextLink != "":
        n = calendar.get(nextLink)
        nextLink = json.loads(n.content.decode()).get("@odata.nextLink", "")
        parsed_n = parse_contents(n)
        parsed_c.extend(parsed_n)
    return parsed_c


# To Do Tasklists
def create_tasklist(title):
    to_do = get_oauth_session()
    request_body = {"displayName": title}
    t = to_do.post("{}/lists".format(todo_api_url), json=request_body)
    return t.ok

def delete_tasklist(tasklist_id):
    to_do = get_oauth_session()
    t = to_do.delete("{}/lists/{}".format(todo_api_url, tasklist_id))
    return t.ok

def update_tasklist(tasklist_id, request_body):
    to_do = get_oauth_session()
    t = to_do.patch("{}/lists/{}".format(todo_api_url, tasklist_id), json=request_body)
    return t.ok


# To Do Tasks
def create_task(tasklist_id, title, request_body={}):
    to_do = get_oauth_session()
    request_body.update({"title": title})
    t = to_do.post("{}/lists/{}/tasks".format(todo_api_url, tasklist_id), json=request_body)
    return t.ok

def delete_task(tasklist_id, task_id):
    to_do = get_oauth_session()
    t = to_do.delete("{}/lists/{}/tasks/{}".format(todo_api_url, tasklist_id, task_id))
    return t.ok

def update_task(tasklist_id, task_id, request_body):
    to_do = get_oauth_session()
    t = to_do.patch("{}/lists/{}/tasks/{}".format(todo_api_url, tasklist_id, task_id), 
    json=request_body)
    return t.ok


# Calendar Events
def create_event(calendar_id, title, request_body={}):
    calendar = get_oauth_session()
    request_body.update({"subject": title})
    c = calendar.post("{}/calendars/{}/events".format(calendar_api_url, calendar_id), json=request_body)
    return c.ok

def delete_event(calendar_id, event_id):
    calendar = get_oauth_session()
    c = calendar.delete("{}/calendars/{}/events/{}".format(calendar_api_url, calendar_id, event_id))
    return c.ok

def update_event(calendar_id, event_id, request_body):
    calendar = get_oauth_session()
