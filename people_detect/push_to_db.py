#!/usr/bin/python

import sqlite3

class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self): 
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

class Db(_name):
    def __init__(self,_name):
        conn = sqlite3.connect(_name)
        print "Opened database %s"%_name

    def create(self, _name):
        conn.execute('''CREATE TABLE Iris_master
                    (Room INT PRIMARY KEY NOT NULL,
                    Name TEXT NOT NULL,
                    Occupany INT NOT NULL,
                    Occupied INTi)''')

    def update(self, _name, room, new_occupied):
        conn.execute('''UPDATE Iris_Master
                    SET Occupied = ? WHERE Room = ?''',
                    (new_occupied, room))

#    def select(self, _name, room, new_occupied):
#        cursor = conn.execute('''SELECT Room, Name, Occupancy, 
#                    Occupied from Iris_master''')
#        
#def main():
#    queue = Queue()
#
##    db = Db.create('test.db')
#
#if __name__ == "__main__":
#    main()
