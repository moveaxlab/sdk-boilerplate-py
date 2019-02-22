from abc import ABC, abstractmethod

from .deserializers import JsonDeserializer
import json


class CallbackHandler(ABC):
    """
    Abstract class to handle callbacks received by the server. It must define a mapping between callbacks namespaces
    and the SdkObject related to the callback body.
    """
    callbacks = {}

    def __init__(self, context):
        self.context = context

    def parse(self, headers, raw_body):
        self._verify(headers, raw_body)
        cb_type = self._get_callback_namespace(raw_body.decode())
        return JsonDeserializer._deserialize_dict(self.callbacks[cb_type], json.loads(raw_body.decode()))

    @abstractmethod
    def _verify(self, headers, raw_body):
        raise NotImplemented("Subclasses must implement this method")

    @abstractmethod
    def _get_callback_namespace(self, raw_body):
        raise NotImplemented("Subclasses must implement this method")
