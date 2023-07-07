from abc import ABC, abstractmethod

class DataManagerInterface(ABC):
    """Abstract class for managing movie data"""
    @abstractmethod
    def get_user_movies(self, user_id):
        pass