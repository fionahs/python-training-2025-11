# Python Coding Questions - Session 3: Recursion & Functions

## Concept Questions
- What is a decorator in Python, and where is it used?
- What's the difference between a generator and a regular function that returns a list?
- When would you choose generators over lists, and what are the memory implications?
- Explain the difference between threading, multiprocessing, and asyncio in Python
- What is the Global Interpreter Lock (GIL)? How does it affect threading and multiprocessing?
- When to use threading, asyncio, multiprocess?
- What are CPU-bound vs IO-bound tasks?
- What's the difference between yield and return in a function
- What's the difference between using open() with explicit close() vs using the with statement
- How to handle exceptions? Why is exception handling important?

---

## Coding Questions
### Coding Problem 1: Docorator

**Problem:**  
Decorator to cache any function return and log hits/misses

**Description:**  
Create a decorator that:
* Caches results for any function with any arguments. (Cache means returning the result directly without calling the function)
* Logs when the function is called
* Logs cache hits
* Logs cache misses

```python
def cache_with_log(func):
    """
    Cache decorator that logs all activity.
    Should work with any function signature.
    """
    
    def wrapper(*args, **kwargs):
        pass
    
    return wrapper

# Test cases
@cache_with_log
def add(a, b):
    """Simple function with positional args"""
    return a + b

@cache_with_log
def greet(name, greeting="Hello"):
    """Function with keyword args"""
    return f"{greeting}, {name}!"

@cache_with_log
def calculate(x, y, operation="add"):
    """Function with mixed args"""
    if operation == "add":
        return x + y
    elif operation == "multiply":
        return x * y


# Run tests
print("=== Test 1: Simple function ===")
print(add(2, 3))      # Should log: Cache MISS for args={args}, kwargs={kwargs}
print(add(2, 3))      # Should log: Cache HIT for args={args}, kwargs={kwargs}
print(add(4, 5))      # Should log: Cache MISS for args={args}, kwargs={kwargs}

print("\n=== Test 2: Function with kwargs ===")
print(greet("Alice"))                    # Should log: Cache MISS for args={args}, kwargs={kwargs}
print(greet("Alice"))                    # Should log: Cache HIT for args={args}, kwargs={kwargs}
print(greet("Bob", greeting="Hi"))       # Should log: Cache MISS for args={args}, kwargs={kwargs}
print(greet("Bob", greeting="Hi"))       # Should log: Cache HIT for args={args}, kwargs={kwargs}

print("\n=== Test 3: Mixed args ===")
print(calculate(3, 4))                   # Should log: Cache MISS for args={args}, kwargs={kwargs}
print(calculate(3, 4, operation="add"))  # Should log: Cache HIT for args={args}, kwargs={kwargs}
print(calculate(3, 4, operation="multiply"))  # Should log: Cache MISS for args={args}, kwargs={kwargs}
```


### Coding Problem 2: Batch Generator

**Problem:**  
Create a generator that takes an iterable and yields items in batches of a specified size.

**Description:**  
```python
def batch(iterable, batch_size):
    """
    Generator that yields items in batches.
    
    Args:
        iterable: Any iterable (list, generator, etc.)
        batch_size: Number of items per batch
    
    Yields:
        Lists of items with length = batch_size (last batch may be smaller)
    
    Example:
        >>> list(batch([1, 2, 3, 4, 5, 6, 7], 3))
        [[1, 2, 3], [4, 5, 6], [7]]
        
        >>> list(batch(range(10), 4))
        [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]
    """

    pass


# Test cases
print(list(batch([1, 2, 3, 4, 5, 6, 7], 3)))
# [[1, 2, 3], [4, 5, 6], [7]]

print(list(batch(range(10), 4)))
# [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]

print(list(batch("ABCDEFGH", 2)))
# [['A', 'B'], ['C', 'D'], ['E', 'F'], ['G', 'H']]
```

### Coding Problem 3: Async Retry with Exponential Backoff


**Problem**
Create a decorator that retries async functions with exponential backoff.


**Description**
```python
import asyncio
import random

def async_retry(max_attempts=3, base_delay=1, backoff_factor=2):
    """
    Decorator that retries async functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of attempts
        base_delay: Initial delay between retries (seconds)
        backoff_factor: Multiply delay by this factor after each retry
    
    Example:
        @async_retry(max_attempts=3, base_delay=1, backoff_factor=2)
        async def unreliable_function():
            # Will retry with delays: 1s, 2s, 4s
            pass
    """
    def decorator():
        # TODO: Implement a decorator with retrying logic with exponential backoff
        # It Will retry with delays: 1s, 2s, 4s if error raises until success

    return decorator


# Flaky API simulator
@async_retry(max_attempts=5, base_delay=0.5, backoff_factor=2)
async def flaky_api_call(success_rate=0.3):
    """
    Simulates an unreliable API call.
    
    Args:
        success_rate: Probability of success (0.0 to 1.0)
    """
    print(f"  Attempting API call...")
    await asyncio.sleep(0.1)  # Simulate network delay
    
    if random.random() < success_rate:
        print("Success!")
        return "API response data"
    else:
        print("Failed!")
        raise ConnectionError("API temporarily unavailable")


async def test_retry():
    print("Test 1: Flaky API (30% success rate)")
    try:
        result = await flaky_api_call(success_rate=0.3)
        print(f"Final result: {result}\n")
    except ConnectionError as e:
        print(f"All retries failed: {e}\n")
    
    print("Test 2: Very flaky API (10% success rate)")
    try:
        result = await flaky_api_call(success_rate=0.1)
        print(f"Final result: {result}\n")
    except ConnectionError as e:
        print(f"All retries failed: {e}\n")


# Run test
# asyncio.run(test_retry())
```