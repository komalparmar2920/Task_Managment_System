import json
import re
from pathlib import Path
from Models import User, Task
from Models.Task import valid_statuses
from exception import (DataFileError,DuplicateIDError,RecordNotFoundError,ValidationError,)

class TaskManager:
    def __init__(self,data_dir=None):
        project_dir = Path(__file__).resolve().parent.parent
        self.data_dir = Path(data_dir) if data_dir else project_dir / "data"
        self.users_file = self.data_dir / "users.json"
        self.tasks_file = self.data_dir / "tasks.json"

        self.Users=[]
        self.Tasks=[]
        self.load_data()

    @staticmethod
    def validate_id(value,label="ID"):
        try:
            result=int(value)
        except(TypeError,ValueError):
            raise ValidationError(f"{label} must be whole number") from None

        if result <= 0:
            raise ValidationError(f"{label} must be greater than zero.")
        return result

    @staticmethod
    def validate_text(value, label):
        value = value.strip() if isinstance(value, str) else ""
        if not value:
            raise ValidationError(f"{label} cannot be empty.")
        return value

    @staticmethod
    def validate_email(email):
        email = TaskManager.validate_text(email, "Email")
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise ValidationError("Please enter a valid email address.")
        return email

    def _read_json(self, path):
        if not path.exists():
            return []

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise DataFileError(
                f"{path.name} contains invalid JSON. Fix or restore the file before continuing."
            ) from error
        except OSError as error:
            raise DataFileError(f"Could not read {path.name}: {error}") from error

        if not isinstance(data, list):
            raise DataFileError(f"{path.name} must contain a JSON list.")
        return data

    def _write_json(self, path, records):
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            temporary_path = path.with_suffix(path.suffix + ".tmp")
            with temporary_path.open("w", encoding="utf-8") as file:
                json.dump(records, file, indent=4, ensure_ascii=False)
            temporary_path.replace(path)
        except OSError as error:
            raise DataFileError(f"Could not write {path.name}: {error}") from error

    def load_data(self):
        # Do not silently replace malformed JSON with empty lists: that could hide data loss.
        raw_users = self._read_json(self.users_file)
        raw_tasks = self._read_json(self.tasks_file)

        try:
            self.users = [User.from_dict(item) for item in raw_users]
            self.tasks = [Task.from_dict(item) for item in raw_tasks]
        except (KeyError, TypeError, ValueError) as error:
            raise DataFileError(f"Stored data has an invalid record: {error}") from error

        user_ids = {user.user_id for user in self.users}
        for task in self.tasks:
            if task.assigned_user_id not in user_ids:
                task.assigned_user_id = None

    def _save_users(self):
        self._write_json(self.users_file, [user.to_dic() for user in self.users])

    def _save_tasks(self):
        self._write_json(self.tasks_file, [task.to_dic() for task in self.tasks])

    def add_user(self, user_id, name, email):
        user_id = self.validate_id(user_id, "User ID")
        name = self.validate_text(name, "Name")
        email = self.validate_email(email)

        if any(user.user_id == user_id for user in self.users):
            raise DuplicateIDError(f"User ID {user_id} already exists.")
        if any(user.email.lower() == email.lower() for user in self.users):
            raise ValidationError("That email address is already registered.")

        user = User(user_id, name, email)
        self.users.append(user)
        try:
            self._save_users()
        except DataFileError:
            self.users.remove(user)
            raise
        return user

    def add_task(self, task_id, title, description):
        task_id = self.validate_id(task_id, "Task ID")
        title = self.validate_text(title, "Task title")
        description = self.validate_text(description, "Task description")

        if any(task.task_id == task_id for task in self.tasks):
            raise DuplicateIDError(f"Task ID {task_id} already exists.")

        task = Task(task_id, title, description)
        self.tasks.append(task)
        try:
            self._save_tasks()
        except DataFileError:
            self.tasks.remove(task)
            raise
        return task

    def get_user(self, user_id):
        user_id = self.validate_id(user_id, "User ID")
        for user in self.users:
            if user.user_id == user_id:
                return user
        raise RecordNotFoundError(f"User ID {user_id} was not found.")

    def get_task(self, task_id):
        task_id = self.validate_id(task_id, "Task ID")
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        raise RecordNotFoundError(f"Task ID {task_id} was not found.")

    def assign_task(self, task_id, user_id):
        task = self.get_task(task_id)
        user = self.get_user(user_id)
        previous_user_id = task.assigned_user_id
        task.assigned_user_id = user.user_id
        try:
            self._save_tasks()
        except DataFileError:
            task.assigned_user_id = previous_user_id
            raise
        return task, user

    def update_status(self, task_id, status):
        task = self.get_task(task_id)
        if status not in valid_statuses:
            raise ValidationError(
                f"Status must be one of: {', '.join(valid_statuses)}."
            )
        previous_status = task.status
        task.status = status
        try:
            self._save_tasks()
        except DataFileError:
            task.status = previous_status
            raise
        return task

    def tasks_for_user(self, user_id):
        user = self.get_user(user_id)
        return user, [
            task for task in self.tasks
            if task.assigned_user_id == user.user_id
        ]

    def assigned_user_name(self, task):
        if task.assigned_user_id is None:
            return "Not Assigned"
        for user in self.users:
            if user.user_id == task.assigned_user_id:
                return user.name
        return "Not Assigned"
        
