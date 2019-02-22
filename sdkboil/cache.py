from abc import ABC, abstractmethod


class CacheInterface(ABC):
    """
    Interface to be implemented by a cache adapter.
    """

    @abstractmethod
    def get(self, key):
        raise NotImplemented('Subclasses must implement this method')

    @abstractmethod
    def set(self, key, value):
        raise NotImplemented('Subclasses must implement this method')

    @abstractmethod
    def delete(self, key):
        raise NotImplemented('Subclasses must implement this method')


# noinspection PyAbstractClass
class CacheAdapter(CacheInterface):
    """
    CacheAdapter superclass. Subclasses must implement the methods defined from the Cache Interface
    """
    pass
