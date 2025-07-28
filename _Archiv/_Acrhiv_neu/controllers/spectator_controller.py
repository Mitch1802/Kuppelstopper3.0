from services.database_service import DatabaseService

class SpectatorController:
    def __init__(self, database_service, settings):
        self.database_service = database_service
        self.settings = settings

    def get_best_for_all(self):
        best = {}
        for a in self.database_service.list_attempts():
            key = (a.group.id, a.lane)
            if key not in best or a.penalized_time < best[key].penalized_time:
                best[key] = a
        return best