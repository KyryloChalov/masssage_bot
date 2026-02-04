def log_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"func {func.__name__} args {args} kwargs {kwargs}")
        return func(*args, **kwargs)
    return wrapper

if __name__ == "__main__":
    @log_decorator
    def foo(a, b, bar=1):
        return a + b + bar


    # Test
    foo(1, 2, bar=1)