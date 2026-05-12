class ProjectState:
    def __init__(self, user_prompt: str):
        self.user_prompt = user_prompt
        self.task_spec = ""
        self.backend_code = ""
        self.frontend_code = ""
        self.review_feedback = ""
        self.iteration = 1
        self.status = "in_progress"  # or "approved"

    def to_dict(self):
        return self.__dict__