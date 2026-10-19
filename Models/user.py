from dataclasses import dataclass
@dataclass
class User:
    user_id:int
    name: str
    email: str

    def to_dic(self):
        return {
            "user_id":self.user_id,
            "name":self.name,
            "email":self.email,
        }

    @classmethod
    def from_dict(cls,data):
        return cls(
            user_id=int(data["user_id"]),
            name=str(data["name"]),
            email=str(data["email"])
        )    