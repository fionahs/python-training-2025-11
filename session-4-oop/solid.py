# SOLID principles

# 1. single responsibility principle (SRP)

# a class should have only one functionality

# Bad example

class User():
    def __init__(self, name):
        self.name = name
    
    def send_email(self):
        print('send email')
    
    def save_to_database(self):
        pass
    
class User():
    def __init__(self, name):
        self.name = name
        
class DatabasePersistence():
    def save(self, user):
        print('save to database')
    
        
class EmailSerivce():
    def send(self, user):
        print(f"send email to {user}")
        
user = User('Steven')
database = DatabasePersistence()
email = EmailSerivce()

email.send(user)
database.save(user)

# 2. Open/close principle (OCP)
# open to entension, close to modification

# bad example
class AreaCalculator:
    def calcualte(self, shape):
        if(shape.type == 'circle'):
            return 3.14 * shape.redius ** 2
        if(shape.type == 'retangle'):
            pass

# Good example
# the Shape -> Retangle & Circle example in the abstract section

# 3. Liskob sustituion principle(LSP)
# subtype must be substituable for the parent type

# Bad example
class Bird:
    def fly(self):
        return 'fly high'
    
class Penguin(Bird):
    def fly(self):
        raise Exception('cannot fly')
    
# Good example
class Bird:
    def move(self):
        return 'fly high'
    
class Sparrow(Bird):
    def move(self):
        print('fly')

class Penguin(Bird):
    def move(self):
        print('move with feet')
        

#4 interface segregation princle (ISP)
# subclass should not be forced to implement the interface they don't use

# Bad example
class Worker:
    def work(self):
        pass

    def eat(self):
        pass

class Human(Worker):
    def work(self):
        print('work')

    def eat(self):
        print('eat')
        
class Robot(Worker):
    def work(self):
        print('work')
    
    def eat(self):
        # raise Exception('cannot eat')
        pass
    
# good example
# Define interface
class Workable():
    def work(self):
        pass
    
class Eatable():
    def eat(self):
        pass

class Human(Workable, Eatable):
    def work(self):
        print('work')

    def eat(self):
        print('eat')

class Robot(Workable):
    def work(self):
        print('work')
        
# 5 Dependency inversion principle (DIP)
# High-level class should not depend low level modules

#bad example
class MySqlDatabase():
    def connect(self):
        return 'connect to mysql'

class PostgresDatabase():
    def connect(self):
        return 'connect to postgres'
    
class UserDatabaseService():
    def __init__(self):
        # self.db = MySqlDatabase() # tightly coupled issue
        self.db = PostgresDatabase() # tightly coupled issue
    
    def connect_to_db(self):
        self.db.connect()
    
# Good Example
class Database():
    def connect(self):
       pass

class MySqlDatabase(Database):
    def connect(self):
        return 'connect to mysql'

class PostgresDatabase(Database):
    def connect(self):
        return 'connect to postgres'

class UserDatabaseService():
    def __init__(self, database):
        self.db = database
    
    def connect_to_db(self):
        self.db.connect()
        
userservice_1 = UserDatabaseService(MySqlDatabase())
userservice_2 = UserDatabaseService(PostgresDatabase())
    
