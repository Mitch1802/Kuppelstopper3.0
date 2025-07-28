from datetime import datetime

class Group:
    def __init__(self, group_id: int, name: str, is_women: bool):
        self.id = group_id
        self.name = name
        self.is_women = is_women

class Attempt:
    def __init__(self, attempt_id: int, group: Group, lane: int, attempt_index: int,
                 time_sec: float, errors: int, timestamp: datetime):
        self.id = attempt_id
        self.group = group
        self.lane = lane
        self.attempt_index = attempt_index
        self.time_sec = time_sec
        self.errors = errors
        self.timestamp = timestamp

    @property
    def penalized_time(self) -> float:
        penalty_per_error = 5.0
        return self.time_sec + self.errors * penalty_per_error