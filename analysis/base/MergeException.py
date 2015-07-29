'''
Created on Jan 6, 2015

@author: markus
'''

class MergeException(Exception):
    """
    Error handling for the merge processes
    """
    
    def __init__(self, message):
        """
        Constructor
        """
        self.__message = message
        
    def __str__(self):
        """
        Make exception a string object
        """
        return self.__message
