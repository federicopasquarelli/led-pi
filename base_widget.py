class Widget:
    def update(self, data, timestamp): pass
    def draw(self, canvas, timestamp): pass
    def activate(self): pass
    def deactivate(self): pass

    @property
    def should_show(self):
        """Return True if this widget wants to be displayed."""
        return False

    @property
    def priority(self):
        """Priority level. Higher numbers take precedence (e.g., 0=Fallback, 10=Active, 100=Emergency)."""
        return 0
