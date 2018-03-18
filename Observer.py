from abc import ABCMeta, abstractmethod
from threading import Condition, RLock


class Observer(object, metaclass=ABCMeta):

    @abstractmethod
    def update(self, *args, **kwargs):
        pass


class Observable:

    def __init__(self):
        self.mutex = RLock()
        self.c = Condition(self.mutex)
        self.observers = []

    def register(self, observer):
        with self.mutex:
            if observer not in self.observers:
                self.observers.append(observer)

    def unregister(self, observer):
        with self.mutex:
            if observer in self.observers:
                self.observers.remove(observer)

    def unregister_all(self):
        with self.mutex:
            if self.observers:
                del self.observers[:]

    def update_observers(self, *args, **kwargs):
        with self.mutex:
            for observer in self.observers:
                self.c.notifyAll()
                observer.update(*args, **kwargs)
