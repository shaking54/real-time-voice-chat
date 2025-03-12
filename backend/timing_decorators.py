import time
import functools
from flask import request, g
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('timing')

class TimingStats:
    """Class to store timing statistics for the current request."""
    def __init__(self):
        self.start_time = time.time()
        self.checkpoints = {}
        self.durations = {}
    
    def checkpoint(self, name):
        """Record a checkpoint time."""
        current = time.time()
        self.checkpoints[name] = current
        elapsed_from_start = current - self.start_time
        logger.info(f"⏱️ {name}: {elapsed_from_start:.3f}s from start")
        
        # Calculate elapsed time from previous checkpoint
        checkpoints = list(self.checkpoints.items())
        if len(checkpoints) > 1:
            prev_name, prev_time = checkpoints[-2]
            elapsed = current - prev_time
            self.durations[f"{prev_name}_to_{name}"] = elapsed
            logger.info(f"⏱️ {prev_name} → {name}: {elapsed:.3f}s")
        
        return current

    def get_summary(self):
        """Get a summary of all timing information."""
        total_time = time.time() - self.start_time
        summary = {
            "total_time": total_time,
            "checkpoints": self.checkpoints,
            "durations": self.durations
        }
        return summary


def initialize_timing():
    """Initialize timing for a request."""
    g.timing = TimingStats()
    return g.timing


def checkpoint(name):
    """Record a checkpoint in the current request timing."""
    if not hasattr(g, 'timing'):
        initialize_timing()
    return g.timing.checkpoint(name)


def timed(description=None):
    """Decorator to time a function execution."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = description or func.__name__
            start_name = f"{func_name}_start"
            end_name = f"{func_name}_end"
            
            if not hasattr(g, 'timing'):
                initialize_timing()
            
            checkpoint(start_name)
            
            try:
                result = func(*args, **kwargs)
                checkpoint(end_name)
                return result
            except Exception as e:
                checkpoint(f"{func_name}_error")
                raise e
        
        return wrapper
    return decorator


def timed_async(description=None):
    """Decorator to time an async function execution."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            func_name = description or func.__name__
            start_name = f"{func_name}_start"
            end_name = f"{func_name}_end"
            
            if not hasattr(g, 'timing'):
                initialize_timing()
            
            checkpoint(start_name)
            
            try:
                result = await func(*args, **kwargs)
                checkpoint(end_name)
                return result
            except Exception as e:
                checkpoint(f"{func_name}_error")
                raise e
        
        return wrapper
    return decorator


def request_timing_middleware(app):
    """Middleware to add timing to all requests."""
    @app.before_request
    def before_request():
        initialize_timing()
        checkpoint("request_received")
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'timing'):
            checkpoint("request_complete")
            summary = g.timing.get_summary()
            logger.info(f"⏱️ Request completed in {summary['total_time']:.3f}s")
            
            # You could add timing headers to the response
            response.headers['X-Processing-Time'] = f"{summary['total_time']:.3f}"
        return response
    
    return app