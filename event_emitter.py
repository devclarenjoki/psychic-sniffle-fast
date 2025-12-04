# event_emitter.py

class EventEmitter:
    """
    A simple event emitter to allow decoupled communication
    between different parts of the application.
    """
    def __init__(self):
        self._listeners = {}

    def on(self, event: str, callback):
        """Register a callback for a given event."""
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)

    def emit(self, event: str, data):
        """Emit an event with data, calling all registered callbacks."""
        if event in self._listeners:
            for callback in self._listeners[event]:
                callback(data)

# Create a singleton instance to be shared across the application
event_emitter = EventEmitter()