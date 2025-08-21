from datetime import timedelta
class Rule:
    id='base'; severity='low'; window=timedelta(minutes=5)
    def consider(self, e): return []
