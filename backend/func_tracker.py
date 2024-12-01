import functools
from typing import Callable, Any

class FunctionTracker:
    _current_websocket = None

    @classmethod
    def set_websocket(cls, websocket):
        """Set the current WebSocket for tracking"""
        cls._current_websocket = websocket

    @classmethod
    def track_function(cls, func: Callable) -> Callable:
        """Decorator to track function execution across files"""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            ws = cls._current_websocket
            if ws:
                try:
                    await ws.send_json({"Function": {func.__name__}})
                except Exception as send_error:
                    print(f"Error sending function tracking: {send_error}")
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                if ws:
                    try:
                        await ws.send_json({"Error" : {str(e)}})
                    except Exception as send_error:
                        print(f"Error sending error tracking: {send_error}")
                raise
        
        return wrapper