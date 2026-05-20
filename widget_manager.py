class WidgetManager:
    def __init__(self, widgets):
        """
        Initialize with a list of widgets.
        The first widget in the list is typically the fallback/default.
        """
        self.widgets = widgets
        self.active_widget = widgets[0]
        self.active_widget.activate()

    def update(self, data, timestamp):
        """
        Update all registered widgets and resolve which one should be active.
        """
        # First, allow all widgets to update their internal state
        for w in self.widgets:
            w.update(data, timestamp)

        # Find the widget with the highest priority that wants to be shown
        best_widget = self.widgets[0] # Default to first widget
        max_priority = -1

        for w in self.widgets:
            if w.should_show:
                if w.priority > max_priority:
                    max_priority = w.priority
                    best_widget = w

        # If the active widget changed, manage the lifecycle transitions
        if best_widget != self.active_widget:
            print(f"Manager: Switching from {self.active_widget.__class__.__name__} to {best_widget.__class__.__name__}")
            self.active_widget.deactivate()
            self.active_widget = best_widget
            self.active_widget.activate()

    def draw(self, canvas, timestamp):
        """
        Render the currently active widget.
        """
        self.active_widget.draw(canvas, timestamp)
