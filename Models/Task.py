from dataclasses import dataclass
from typing import Optional

valid_statuses=("Pending","In Progress","Completed")

@dataclass
class Task:
    task_id:int | None
    title:str
    description:str
    status:str="Pending"
    assigned_user_id:Optional[int]=None

    def to_dic(self):
        return{
            "task_id":self.task_id,
            "title":self.title,
            "description":self.description,
            "status":self.status,
            "assigned_user_id":self.assigned_user_id,
        }

    @classmethod
    def from_dict(cls,data):
        status=str(data.get("status","Pending"))
        if status not in valid_statuses:
            status="Pending"

        assigned_user_id=data.get("assigned_user_id")        
        if assigned_user_id is not None:
            assigned_user_id=int(assigned_user_id)

        return cls(
            task_id=int(data["task_id"]),
            title=str(data["title"]),
            description=str(data["description"]),
            status=status,
            assigned_user_id=assigned_user_id,
        )    