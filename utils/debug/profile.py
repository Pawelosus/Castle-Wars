import cProfile
import io
import pstats

def profile(func):
    """Decorator to profile a function."""
    def wrapper(*args, **kwargs):
        # Create a StringIO object to capture the output
        pr = cProfile.Profile()
        pr.enable()  # Start profiling
        result = func(*args, **kwargs)  # Call the function
        pr.disable()  # Stop profiling
        
        # Capture the profile stats
        s = io.StringIO()
        pstats.Stats(pr, stream=s).sort_stats('cumtime').print_stats()  # Sort by cumulative time
        print(s.getvalue())  # Print the profiling results
        
        return result
    
    return wrapper
