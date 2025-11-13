'''
# Iterable
Eg: list, tuple, dict, str

has __iter__

# Iterator

has __iter__ and __next__

iterator_list = iter(list)

# Generator
special iterator

 use "yield" to be a generator function
 

'''

my_list = [1, 2, 3]
iterator = iter(my_list)
print(next(iterator))
print(next(iterator))
print(next(iterator))
# print(next(iterator)) # raise StopIteration error

print(type(my_list))
print(type(iter(my_list)))

for x in my_list:
    print(x)

'''
What for loops do behind the scene

iterator = iter(my_list)

While True:
    try:
        x = next(iterator)
    except StopIteration:
        break
    else:
        print(x)

'''


class Counter:
    def __init__(self):
        self.current = 0
        self.max = 5

    def __iter__(self):
        return self

    def __next__(self):
        if self.current < self.max:
            self.current += 1
            return self.current

        raise StopIteration


c = Counter()

for i in c:
    print(f'my counter: {i}')


# generator

def fibonacci(limit):
    a = 0
    b = 1
    while a < limit:
        yield a  # turn the function into a generator
        a, b = b, a + b


def my_generator():
    yield 'first'
    yield 'second'
    yield 'third'


generator = my_generator()
print(next(generator))
print(next(generator))
print(next(generator))

f = fibonacci(5)
print(next(f))
print(next(f))
print(next(f))
print(next(f))
# print(next(generator))

# generator comprehension expression

numbers = [1, 2, 3, 4, 5]
squares = (x ** 2 for x in numbers)


