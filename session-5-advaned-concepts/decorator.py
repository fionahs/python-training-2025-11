# decorator
# reuse the logic / functions to functions
import time

def log_performance(level="INFO"):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            print(f'[{level}] {func.__name__} is taking {end - start:.4f} seconds')
            return result

        return wrapper
    return decorator

def my_decorator(func):
    def wrapper():
        # reuse logic
        print('my decorator is called')
        func()
    
    return wrapper

@my_decorator
@log_performance()
def fun1():
    # log_performance_func()
    # log the performance code
    print('func1')
    n = 0
    for i in range(100000):
      n +=1    

def fun2():
    # log_performance_func()
    # log the performance code
    pass

def fun3():
     # log the performance code
    pass

# new_func1 = my_decorator(fun1)
# new_func1()
fun1()


# high order function
# def enhance_with_log_performance(func):
    
#     def new_func():
#         # reuse logic
#         func()
    
#     return new_func

# new_func = enhance_with_log_performance(fun1)
# new_func2 = enhance_with_log_performance(fun2)