from exception import (DataFileError,DuplicateIDError,RecordNotFoundError,TaskManagementError,ValidationError,)
from service import TaskManager
from Models.Task import valid_statuses
def read_text(prompt):
    value = input(prompt).strip()
    if not value and not allow_empty:
        raise ValidationError("Input cannot be empty.")
    return value    
def read_id(prompt):
    return input(prompt).strip()
def show_users(manager):
    if not manager.users:
        print("No users available")
        return
    print("Users")
    for user in manager.users:
        print(f"ID: {user.user_id} | Name: {user.name} | Email: {user.email}")

def show_tasks(manager,tasks=None):
    if tasks is None:
        tasks = manager.tasks

    if not tasks:
        print("No tasks available.")
        return

    print("Tasks")
    for task in tasks:
        print(f"Task ID: {task.task_id}")
        print(f"Title: {task.title}")
        print(f"Description: {task.description}")
        print(f"Status: {task.status}")
        print(f"Assigned To: {manager.assigned_user_name(task)}")


    

def add_user(manager):
    user = manager.add_user(
        read_id("Enter User ID: "),
        read_text("Enter User Name: "),
        read_text("Enter Email: "),
    )
    print(f"User '{user.name}' added successfully.")

def add_task(manager):
    task=manager.add_task(
        read_id("Enter Task ID:"),
        read_text("Enter Task Title:"),
        read_text("Enter Task Description: "),
    )
    print(f"Task '{task.title}' added successfully")

def assign_task(manager):
    task, user = manager.assign_task(
        read_id("Enter Task ID: "),
        read_id("Enter User ID: "),
    )
    print(f"Task '{task.title}' assigned to {user.name} successfully.")


def update_status(manager):
    task_id=read_id("Enter Task ID: ")
    print("1. Pending")
    print("2. In Progress")
    print("3. Completed")
    choices = {"1": "Pending", "2": "In Progress", "3": "Completed"}
    choice = read_id("Select new status: ").strip()

    if choice not in choices:
        raise ValidationError("Invalid status choice. Select 1, 2, or 3.")

    task = manager.update_status(task_id, choices[choice])
    print(f"Task status updated to '{task.status}'.")

def search_task(manager):
    query=read_id("Enter Task ID or title to search: ").casefold()
    matches=[
        task for task in manager.tasks
        if str(task.task_id).casefold()==query or query in str(task.title).casefold()
    ]
    if not matches:
        print("No matching tasks found.")
        return
    show_tasks(manager, matches)

def edit_task(manager):
    task_id=read_id("Enter Task ID to edit: ")
    task=manager.get_task(task_id)
    
    print("Leave fields blank to keep current values.")
    print(f"Current Title: {task.title}")
    title=read_text("Enter new title: ").strip()
    print(f"Current Description: {task.description}")
    description=read_text("Enter new description: ").strip()
    update={}
    if title:
        update["title"]=title
    if description:
        update["description"]=description
    if not update:
        print("No changes made.")
        return

    updated_task=manager.edit_task(task_id, **update)
    print(f"Task '{updated_task.title}' updated successfully.")

def delete_task(manager):
    task_id=read_id("enter Task id to delete:")
    task=manager.get_task(task_id)
    print(f"Task: {task.title}")
    confirm=read_id("Are you sure you want to delete this task? (y/n): ").casefold()

    if confirm not in ("y", "yes"):
        print("Deletion cancelled.")
        return

    manager.delete_task(task_id)
    print(f"Task '{task.title}' deleted successfully.")

def show_user_tasks(manager):
    user, tasks = manager.tasks_for_user(read_id("Enter User ID: "))
    print(f"\nTasks of {user.name}")

    if not tasks:
        print("No tasks assigned to this user.")
        return

    show_tasks(manager, tasks)    

    """for task in tasks:
        print(f"ID: {task.task_id} | Title: {task.title} | Status: {task.status}")"""

def main():
    try:
        manager=TaskManager()
    except DataFileError as error:
        print(f"Could not load saved data: {error}")
        print("Correct the data file before restarting the application.")
        return
    actions = {
        "1": lambda: add_user(manager),
        "2": lambda: add_task(manager),
        "3": lambda: show_users(manager),
        "4": lambda: show_tasks(manager),
        "5": lambda: assign_task(manager),
        "6": lambda: update_status(manager),
        "7": lambda: search_task(manager),
        "8": lambda: show_user_tasks(manager),
        "9": lambda: edit_task(manager),
        "10": lambda: delete_task(manager),
    }

    while True:
        print("Task Management System")
        print("1. Add User")
        print("2. Add Task")
        print("3. Display Users")
        print("4. Display All Tasks")
        print("5. Assign Task to User")
        print("6. Update Task Status")
        print("7. Search Task")
        print("8. Show User Tasks")
        print("9. Edit Task")
        print("10. Delete Task")
        print("11. Exit")

        try:      
            choice = input("Enter your choice: ").strip()

            if choice == "11":
                print("Goodbye!")
                break

            action = actions.get(choice)
            if action is None:
                print("Invalid choice! Select 1 to 11.")
                continue

        
            action()
        except (ValidationError, DuplicateIDError, RecordNotFoundError) as error:
            print("Operation failed:", error)
        except DataFileError as error:
            print("Data could not be saved or read:", error)
        except TaskManagementError as error:
            print("Task management error:", error)
        except (EOFError, KeyboardInterrupt):
            print("\nApplication closed.")
            break

        except (TypeError, ValueError) as error:
            print(f"Invalid input: {error}")    


if __name__ == "__main__":
    main()
 