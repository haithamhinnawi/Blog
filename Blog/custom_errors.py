
class BlockedError(Exception):
    def __init__(self, detail=None):
        self.detail = detail or "You are blocked"
        super().__init__(self.detail)

class ReachedLimitError(Exception):
    def __init__(self, detail=None):
        self.detail = detail or "You have reached limit of add posts today"
        super().__init__(self.detail)