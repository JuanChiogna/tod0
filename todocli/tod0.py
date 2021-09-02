from datetime import datetime
from todocli import auth, interface
import re

class ToDo():
    def __init__(self):
        self.load_lists()

    # Load all tasklists
    def load_lists(self):
        self.tasklists = []
        tasklist_data = auth.list_tasklists()
        for data in tasklist_data:
            tasklist = Tasklist(data)
            self.tasklists.append(tasklist)
        self.tasklist_ids = [tasklist.id for tasklist in self.tasklists]
        self.tasklist_names = [tasklist.displayName for tasklist in self.tasklists]

    # Load all tasks for every tasklist
    def load_tasks(self):
        for tasklist in self.tasklists:
            tasklist.load_tasks()
        pass

    # Returns tasklist instance if found by name  
    def tasklist_by_name(self, tasklist_name):
        if tasklist_name in self.tasklist_names:
            index = self.tasklist_names.index(tasklist_name)
            return self.tasklists[index]
        else:
            print(f">> No tasklist with name '{tasklist_name}' exists")
            return None

    # Returns tasklist instance if found by id
    def tasklist_by_id(self, tasklist_id):
        if tasklist_id in self.tasklist_ids:
            index = self.tasklist_ids.index(tasklist_id)
            return self.tasklists[index]
        else:
            print(f">> No tasklist with id '{tasklist_id}' exists")
            return None

    # Moves a task from tasklist 1 to tasklist 2
    def move_task(self, tasklist_id_1, tasklist_id_2, task_id):
        # Avoid moving to the same tasklist and check that both tasklists exist
        if (tasklist_id_1 == tasklist_id_2) or (tasklist_id_1 not in self.tasklist_ids or tasklist_id_2 not in self.tasklist_ids):
            return False
        tasklist_1 = self.tasklist_by_id(tasklist_id_1)
        tasklist_2 = self.tasklist_by_id(tasklist_id_2)
        task = tasklist_1.task_by_id(task_id)
        # Check that the task exists
        if task is None:
            return False
        # Create a copy of the task at the new list
        if auth.create_task(tasklist_id_2, task.title, task.data):
            # Delete the task at the previous list
            tasklist_1.delete_task(task_id, silent=True)
            print(f">> Moved task '{task.title}' from '{tasklist_1.displayName}' to '{tasklist_2.displayName}'.")
            return True
        else:
            print(f">> Could not move task '{task.title}' from '{tasklist_1.displayName}' to '{tasklist_2.displayName}'.")
            return False

    # Deletes a given tasklist from To Do
    def delete_tasklist(self, tasklist_id):
        if tasklist_id not in self.tasklist_ids:
            print(f">> No tasklist with id '{tasklist_id}' exists")
            return False
        tasklist = self.tasklist_by_id(tasklist_id)
        if auth.delete_tasklist(tasklist_id):
            print(f">> Deleted tasklist '{tasklist.displayName}'.")
            index = self.tasklists.index(tasklist)
            self.tasklists.pop(index)
            self.tasklist_ids.pop(index)
            self.tasklist_names.pop(index)
            return True
        else:
            print(f">> Could not delete tasklist '{tasklist.displayName}'.")
            return False


class Tasklist():
    def __init__(self, data):
        self.data = data
        self.displayName = data.get('displayName', '')
        self.id = data.get('id', '')
        # self.load_tasks()

    # Load all tasks
    def load_tasks(self):
        self.tasks = []
        task_data = auth.list_tasks(self.id)
        for data in task_data:
            task = Task(self.displayName, self.id, data)
            if task.status != "completed":
                self.tasks.append(task)
        self.task_names = [task.title for task in self.tasks]
        self.task_ids = [task.id for task in self.tasks]

    # Returns task instance if found by name
    def task_by_name(self, task_name):
        if task_name in self.task_names:
            index = self.task_names.index(task_name)
            return self.tasks[index]
        else:
            print(f">> No task with name '{task_name}' exists in '{self.displayName}'.")
            return None

    # Returns task instance if found by id
    def task_by_id(self, task_id):
        if task_id in self.task_ids:
            index = self.task_ids.index(task_id)
            return self.tasks[index]
        else:
            print(f">> No task with id '{task_id}' exists in '{self.displayName}'.")
            return None

    # Updates the current title
    def change_title(self, title):
        old_title = self.displayName
        self.displayName = title
        request_body = {"displayName": title}
        if auth.update_tasklist(self.id, request_body):
            print(f">> Updated tasklist title from '{old_title}' to '{title}'.")
        else:
            print(f">> Could not update tasklist title from '{old_title}' to '{title}'.")

    # Returns True if there are still tasks due today that haven't been moved yet
    def tasks_remaining(self):
        done = True
        today = date_today()
        for task in self.tasks:
            if task.dueDate == today:
                done = False
        return not done

    # Creates a new task
    def create_task(self, title):
        if auth.create_task(self.id, title):
            self.load_tasks()
            return True
        else:
            return False

    # Deletes a given task from the tasklist
    def delete_task(self, task_id, silent=False):
        if task_id not in self.task_ids:
            print(f">> No task with id '{task_id}' exists in '{self.displayName}'")
            return False
        task = self.task_by_id(task_id)
        if auth.delete_task(self.id, task_id):
            if not silent:
                print(f">> Deleted task '{task.title}' from  tasklist '{self.displayName}'.")
            index = self.tasks.index(task)
            self.tasks.pop(index)
            self.task_ids.pop(index)
            self.task_names.pop(index)
            return True
        else:
            if not silent:
                print(f">> Could not delete task '{task.title}' from the list '{self.displayName}'.")
            return False


class Task():
    def __init__(self, tasklist_displayName, tasklist_id, data):
        self.data = data
        self.title = data.get('title', '')
        self.parent_name = tasklist_displayName
        self.status = data.get('status', '')
        self.createdDateTime = data.get('createdDateTime', '')
        self.lastModifiedDateTime = data.get('lastModifiedDateTime', '')
        self.id = data.get('id', '')
        self.parent_id = tasklist_id
        self.body = data.get('body', '')
        self.dueDateTime = data.get('dueDateTime', '')
        self.dueDate = parse_date(self.data)

    # Toggles task's state between checked and unchecked
    def toggle(self):
        if self.status == "completed":
            # If it's checked, uncheck it
            if auth.update_task(self.parent_id, self.id, {"status": "notStarted"}):
                self.status = "notStarted"
                print(f">> Changed status of '{self.title}' from 'completed' to 'notStarted'.")
            else:
                print(f">> Could not change status of '{self.title}' from 'completed' to 'notStarted'.")
        elif self.status == "notStarted":
            # If it's unchecked, check it
            if auth.update_task(self.parent_id, self.id, {"status": "completed"}):
                self.status = "completed"
                print(f">> Changed status of '{self.title}' from 'notStarted' to 'completed'.")
            else:
                print(f">> Could not change status of '{self.title}' from 'notStarted' to 'completed'.")
        else:
            input(f">> Can't do or undo task: {self.title}.")

    # Sets a due date for a task given in format "dd-mm-yyyy"
    def set_due_date(self, dueDate):
        reversed_dueDate = reverse_date(dueDate)
        request_body = {"dueDateTime": {"dateTime": f"{reversed_dueDate}T03:00:00.0000000", "timeZone": "UTC"}}
        if auth.update_task(self.parent_id, self.id, request_body):
            print(f">> Set due date of task '{self.title}' to '{dueDate}'.")
            return True
        else:
            print(f">> Could not set due date of task '{self.title}' to '{dueDate}'.")
            return False


# Returns today's date in format "dd-mm-yyyy"
def date_today():    
    dt = datetime.today()
    day, month, year = [f"0{x}" if len(str(x)) < 2 else f"{x}" for x in (dt.day, dt.month, dt.year)]
    return "-".join([day, month, year])

# Takes a task's request_body json and returns its due date in format "dd-mm-yyyy"
def parse_date(argument):
    # If argument is a json dict, parse the date from it
    if type(argument) is dict:
        request_body = argument
        date_dict = request_body.get("dueDateTime", {})
        if date_dict != {}:
            date = date_dict.get("dateTime", "")
            date = date.replace("T00:00:00.0000000", "")
            date = date.replace("T03:00:00.0000000", "")
        else:
            date = ""
        return reverse_date(date)

    # If argument is a string, parse the date from it
    elif type(argument) is str:
        text = argument
        # Re match. Matches "dd/mm/yy" pattern on tasks 
        match = re.search("((\d+)\/(\d+)(\/(\d+))?)", text)
        if match is None:
            return None
        else:
            date = match.group(1)
            day = match.group(2)
            month = match.group(3)
            year = match.group(5)
            if year is None:
                year = date_today().split("-")[2]
            elif len(year) == 2:
                year = f"20{year}"
            day, month, year = [f"0{x}" if len(str(x)) < 2 else f"{x}" for x in (day, month, year)]
            date = "-".join([day, month, year])
            return date

# Takes a date with format "yyyy-mm-dd" and returns "dd-mm-yyyy" or vice versa
def reverse_date(date):
    reversed_date = date.split("-")
    reversed_date.reverse()
    reversed_date = "-".join(reversed_date)
    return reversed_date


# Moves all tasks with due date today to the list given
def move_tasks_by_date():
    print(">> Loading tasks . . .")
    to_do = ToDo()
    to_do.load_tasks()
    print(">> Tasks loaded successfully")
    print(f">> Today's date is {date_today()}")


    # Default list name
    default_list = to_do.tasklist_by_name("Tareas")
    
    for tasklist in to_do.tasklists:
        if tasklist.id == default_list.id:
            continue
        loop = 0
        while tasklist.tasks_remaining():
            for task in tasklist.tasks:
                if task.dueDate == date_today():
                    to_do.move_task(tasklist.id, default_list.id, task.id)
            loop += 1
            if loop >= 50:
                print(f">> Stuck on infinite loop on list {tasklist.displayName}")
                return
    print(">> Done!")


# Creates a quick task
def quick_task():
    title = interface.run()
    if title is None:
        return
    to_do = ToDo()
    # Default list name
    default_list = to_do.tasklist_by_name("Tareas")
    date = parse_date(title)
    default_list.create_task(title)
    print(f">> Task '{title}' created successfully")
    if date is not None:
        print(f">> Date recognized: {date}")
        task = default_list.task_by_name(title)
        task.set_due_date(date)