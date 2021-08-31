import auth
import time
from datetime import datetime

class Tasklist():
    def __init__(self, data):
        self.data = data
        self.displayName = data.get('displayName', '')
        self.id = data.get('id', '')
        self.get_tasks()

    def delete(self):
        # Deletes the tasklist from To Do
        if auth.delete_tasklist(self.id):
            print(f">> Deleted tasklist '{self.displayName}'.")
            return True
        else:
            print(f">> Could not delete tasklist '{self.displayName}'.")
            return False

    def change_title(self, title):
        # Updates the current title
        old_title = self.displayName
        self.displayName = title
        request_body = {"displayName": title}
        if auth.update_tasklist(self.id, request_body):
            print(f">> Updated tasklist title from '{old_title}' to '{title}'.")
        else:
            print(f">> Could not update tasklist title from '{old_title}' to '{title}'.")

    def get_tasks(self):
        # Loads all tasks from the tasklist
        # print("\n" + self.displayName + "\n")
        self.tasks = []
        task_data = auth.list_tasks(self.id)
        for tsk in task_data:
            task = Task(self.displayName, self.id, tsk)
            if task.status != "completed":
                # print("    " + task.title)
                # print(task.dueDateTime)
                # if task.dueDateTime != "":
                #     print()
                self.tasks.append(task)

    def tasks_remaining(self):
        done = True
        for task in self.tasks:
            if task.dueDate == date_today and self.displayName != "Tareas":
                done = False
        return not done

    def delete_task(self, task_id, move_task=False):
        # Deletes a given task from the tasklist
        task = task_by_id(self.id, task_id)
        if task is None:
            return
        idx = self.tasks.index(task)
        if task.delete():
            if not move_task:
                print(f">> Deleted task '{task.title}' from  tasklist '{self.displayName}'.")
            self.tasks.pop(idx)
            return True
        else:
            if not move_task:
                print(f">> Could not delete task '{task.title}' from the list '{self.displayName}'.")
            return False


class Task():
    def __init__(self, tasklist_displayName, tasklist_id, data):
        self.data = data
        self.title = data.get('title', '')
        self.tasklist_displayName = tasklist_displayName
        self.status = data.get('status', '')
        self.createdDateTime = data.get('createdDateTime', '')
        self.lastModifiedDateTime = data.get('lastModifiedDateTime', '')
        self.id = data.get('id', '')
        self.tasklist_id = tasklist_id
        self.body = data.get('body', '')
        self.dueDateTime = data.get('dueDateTime', '')
        self.dueDate = get_date(self.data)

    def toggle(self):
        # Toggles task between checked and unchecked
        if self.status == "completed":
            # If it's checked, uncheck it
            if auth.update_task(self.tasklist_id, self.id, {"status": "notStarted"}):
                self.status = "notStarted"
                print(f">> Changed status of '{self.title}' from 'completed' to 'notStarted'.")
            else:
                print(f">> Could not change status of '{self.title}' from 'completed' to 'notStarted'.")
        elif self.status == "notStarted":
            # If it's unchecked, check it
            if auth.update_task(self.tasklist_id, self.id, {"status": "completed"}):
                self.status = "completed"
                print(f">> Changed status of '{self.title}' from 'notStarted' to 'completed'.")
            else:
                print(f">> Could not change status of '{self.title}' from 'notStarted' to 'completed'.")
        else:
            input(f">> Can't do or undo task: {self.title}.")

    def delete(self):
        # Deletes the task from To Do
        if auth.delete_task(self.tasklist_id, self.id):
            return True
        else:
            return False

    def set_due_date(self, dueDate):
        # Sets a due date for a task given in format "dd-mm-yyyy"
        reversed_dueDate = reverse_date(dueDate)
        request_body = {"dueDateTime": {"dateTime": f"{reversed_dueDate}T03:00:00.0000000", "timeZone": "UTC"}}
        if auth.update_task(self.tasklist_id, self.id, request_body):
            print(f">> Setted due date of task '{self.title}' to '{dueDate}'.")
            return True
        else:
            print(f">> Could not set due date of task '{self.title}' to '{dueDate}'.")
            return False


class Calendar():
    pass


class Event():
    pass

def tasklist_by_name(name):
    # Returns tasklist instance if found by name
    global tasklists
    for tasklist in tasklists:
        if tasklist.displayName == name:
            return tasklist
    else:
        print(f">> No tasklist with name '{name}' exists.")
        return None

def tasklist_by_id(tasklist_id):
    # Returns tasklist instance if found by id
    global tasklists
    for tasklist in tasklists:
        if tasklist.id == tasklist_id:
            return tasklist
    else:
        print(f">> No tasklist with id '{tasklist_id}' exists.")
        return None

def task_by_name(tasklist_id, name):
    # Returns task instance if found by name
    tasklist = tasklist_by_id(tasklist_id)
    for task in tasklist.tasks:
        if task.title == name:
            return task
    else:
        print(f">> No task with name '{name}' exists in '{tasklist.displayName}'.")
        return None

def task_by_id(tasklist_id, task_id):
    # Returns task instance if found by id
    tasklist = tasklist_by_id(tasklist_id)
    for task in tasklist.tasks:
        if task.id == task_id:
            return task
    else:
        print(f">> No task with id '{task_id}' exists in '{tasklist.displayName}'.")
        return None


def load_lists():
    # Loads all tasklists and their respective tasks
    tasklists = []
    tasklist_data = auth.list_tasklists()
    for lst in tasklist_data:
        tasklist = Tasklist(lst)
        tasklists.append(tasklist)
    return tasklists


def move_task(tasklist_id_1, tasklist_id_2, task_id):
    # Moves a task from tasklist 1 to tasklist 2
    global tasklists
    # Avoid moving to the same tasklist
    if tasklist_id_1 == tasklist_id_2:
        return False
    tasklist_1 = tasklist_by_id(tasklist_id_1)
    tasklist_2 = tasklist_by_id(tasklist_id_2)
    # Check that both tasklists exist
    if tasklist_1 is None or tasklist_2 is None:
        return False
    task = task_by_id(tasklist_id_1, task_id)
    # Check that the task exists
    if task is None:
        return False
    # Create a copy of the task at the new list
    if auth.create_task(tasklist_id_2, task.title, task.data):
        # Delete the task at the previous list
        tasklist_1.delete_task(task_id, move_task=True)
        print(f">> Moved task '{task.title}' from '{tasklist_1.displayName}' to '{tasklist_2.displayName}'.")
        return True
    else:
        print(f">> Could not move task '{task.title}' from '{tasklist_1.displayName}' to '{tasklist_2.displayName}'.")
        return False
    

def get_date(request_body):
    # Takes a task's request_body and returns its due date in format "dd-mm-yyyy"
    date_dict = request_body.get("dueDateTime", {})
    if date_dict != {}:
        date = date_dict.get("dateTime", "")
        date = date.replace("T00:00:00.0000000", "")
        date = date.replace("T03:00:00.0000000", "")
    else:
        date = ""
    return reverse_date(date)

def reverse_date(date):
    # Takes a date with format "yyyy-mm-dd" and returns "dd-mm-yyyy" or vice versa
    reversed_date = date.split("-")
    reversed_date.reverse()
    reversed_date = "-".join(reversed_date)
    return reversed_date

def run():
    # 1.1 Load tasks
    global tasklists
    print(">> Loading tasks . . .")
    tasklists = load_lists()
    print(">> Tasks loaded successfully")

    # 1.2 Load events

    # 2. Get DateTime format of today
    global date_today
    dt = datetime.today()
    day, month, year = [f"0{x}" if len(str(x)) < 2 else f"{x}" for x in (dt.day, dt.month, dt.year)]
    date_today = "-".join([day, month, year])
    print(f">> Today's date is {date_today}")

    # 3.1 Move tasks accordingly
    tareas = tasklist_by_name("Tareas")
    for tasklist in tasklists:
        loop = 0
        while tasklist.tasks_remaining():
            for task in tasklist.tasks:
                if task.dueDate == date_today:
                    move_task(tasklist.id, tareas.id, task.id)
            loop += 1
            if loop >= 50:
                print(f">> Stuck on infinite loop on list {tasklist.displayName}")
                break
    print(">> Done!")

    # 3.2 Create events accordingly