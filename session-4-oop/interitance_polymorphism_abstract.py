from abc import ABC, abstractmethod
# Inheritance
# allow a class to acquire properties and methods from another class

class Animal:
    def __init__(self, name):
        self.name = name
        
    def speak(self):
        print(f"{self.name} make a sound")
        
    def eat(self, food):
        print(f"{self.name} is eating {food}")
        
class Dog(Animal):
    
    def __init__(self, name, type):
        super().__init__(name)
        self.type = type
        
    # overriding parent class method
    def speak(self):
        #  super().speak() call parent method
        print(f"{self.name} of {self.type} make a woof!")
        
class Cat(Animal):
    def speak(self):
        print(f"{self.name} make a meow!")

dog_1 = Dog('Max', 'Golden doodle')

print(dog_1.name)
dog_1.eat('bone')
dog_1.speak()

cat_1 = Cat('Sophie')
cat_1.speak()
cat_1.eat('fish')


class A:
    def greet(self):
        print('A')
        
        
class B:
    def greet(self):
        print('B')

    def run(self):
        print('run')
        
# similar to the implemente in other OOP        
class C(A, B):
    pass

c = C()
c.greet()
c.run()


## Polymorphism & abstract
# same method, different implementation in different class
# Abstract - define the interface, not implementation

class BadCircle:
    def __init__(self, radius):
        self.radius = radius
    
    def circle_area(self):
        return 3.14 * self.radius**2

    def circle_perimeter(self):
        return 2 * 3.13 * self.radius

class BadRetangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
    def retangle_area(self):
        return self.width * self.height

    def retangle__perimeter(self):
        return 2* (self.width + self.height)



# abstract interface
# inherite Abstract Base Class
class Shape(ABC):
    
    @abstractmethod
    def area(self):
        pass
    
    @abstractmethod
    def perimeter(self):
        pass

# shape_1 = Shape() raise error!
    
class Retangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2* (self.width + self.height)
    
class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14 * self.radius**2

    def perimeter(self):
        return 2 * 3.13 * self.radius
    
# retangle = BadRetangle(1,1)
# circle = BadCircle(2)

retangle = Retangle(1,1)
circle = Circle(2)

shapes = [retangle, circle]

for shape in shapes:
    print(shape.area())
    print(shape.perimeter())
    