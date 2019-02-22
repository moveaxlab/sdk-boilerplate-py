from abc import ABC, abstractmethod


class Hook(ABC):
    """
    Hook Interface class. Classes Implementing the Hook Class should define a run method which is called during the run
    of a request based on the extended Hook Subclass. This class should not be extended itself
    """

    @abstractmethod
    def run(self):
        raise NotImplemented("Subclasses must implement this method")


# noinspection PyAbstractClass
class PresendHook(Hook):
    """
    Class defining an hook which will be run before the request is sent
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request


# noinspection PyAbstractClass
class FailureHook(Hook):
    """
    Class defining an hook which will be run when receiving a response with status code > 299
    """

    def __init__(self, context, request, response, exception):
        self.context = context
        self.request = request
        self.response = response
        self.exception = exception


# noinspection PyAbstractClass
class SuccessHook(Hook):
    """
    Class defining an hook which will be run when receiving a response with 200 <= status code <= 299
    """

    def __init__(self, context, request, response):
        self.context = context
        self.request = request
        self.response = response
