# Design Patterns

# 1. Singleton pattern
# database_instance = Database()

class Logger:
    # def __init__
    _instance = None
    
    def __new__(cls):
        if(cls._instance is None):
            cls._instance = super().__new__(cls)
            cls._instance.logs = []

        return cls._instance
    
    def log(self, message):
        self.logs.append(message)
        print(f"log: {message}")
    
    

logger1 = Logger()
# logger2 = Logger()


# 2. Factory pattern
# create objects without giving exact class to create

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

class AnimalFactory:
    def create_animal(type):
        if type == 'cat':
            return Cat()
        elif type == 'dog':
            return Dog()
        #...

AnimalFactory.create_animal('cat')
AnimalFactory.create_animal('dog')


# 3 Observer Pattern
# Define one-to-many system for notifying the multiple clients of new changes
# use case: event system, notification system

class Newletter:
    def __init__(self, system_name):
        self.system_name = system_name
        self.subscribers = []
        
    def subscribe(self, email, callback_func):
        self.subscribers.append((email, callback_func))
        print(f"{email} subscribed to {self.system_name}")
        
    def unscubscribe(self, email):
        self.subscribers.remove(email)
    
    def publish_news(self, news):
        for email, callback_func in self.subscribers:
            # process code to send email
            print(f'Sending email to {email}: {news}')
            callback_func(news)
            
            
