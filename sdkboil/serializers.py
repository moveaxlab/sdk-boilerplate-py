import json

from abc import ABC, abstractmethod

from .object import SdkObject, SdkCollectionObject
from .exception import MissingContentTypeException, UnknownContentTypeException, InvalidObjectClassException
from .headers import APPLICATION_FORM_URLENCODED, APPLICATION_JSON


def _get_serializer(content_type):
    if not content_type:
        raise MissingContentTypeException("Cannot get correct serializer without defining the Content-Type")
    elif content_type == APPLICATION_JSON:
        return JsonSerializer
    elif content_type == APPLICATION_FORM_URLENCODED:
        return FormSerializer
    else:
        raise UnknownContentTypeException("Unsupported Content-Type: {}".format(content_type))


class Serializer(ABC):
    @staticmethod
    @abstractmethod
    def serialize(obj):
        raise NotImplemented("Subclasses must implement this method")


class JsonSerializer(Serializer):
    @staticmethod
    def serialize(obj):
        if isinstance(obj, SdkObject):
            return json.dumps(JsonSerializer._serialize_subdicts(obj.__dict__))
        elif isinstance(obj, SdkCollectionObject):
            return json.dumps(JsonSerializer._serialize_array(obj))
        else:
            return json.dumps(obj)

    @staticmethod
    def _serialize_subdicts(dict_):
        """
        Helper method to serialize recursively every nested SdkObject into their json serialization.
        """
        json_dict = {}
        for key, value in dict_.items():
            if isinstance(value, SdkObject):
                json_dict[key] = JsonSerializer._serialize_subdicts(value.__dict__)
            elif isinstance(value, dict):
                json_dict[key] = JsonSerializer._serialize_subdicts(value)
            elif isinstance(value, list):
                json_dict[key] = JsonSerializer._serialize_array(value)
            else:
                json_dict[key] = value
        return json_dict

    @staticmethod
    def _serialize_array(array):
        """
        Helper method to serialize every SdkObject contained in a list field into its json serialization.
        It parses nested dicts and list recursively (if any)
        """
        if array:
            el = array[0]
            if isinstance(el, SdkObject):
                array = [JsonSerializer._serialize_subdicts(el.__dict__) for el in array]
            elif isinstance(el, dict):
                array = [JsonSerializer._serialize_subdicts(el) for el in array]
            elif isinstance(el, list):
                array = JsonSerializer._serialize_array(array)
        return array


# noinspection PyAbstractClass
class FormSerializer(Serializer):
    @staticmethod
    def serialize(obj):
        if isinstance(obj, SdkObject):
            return obj.__dict__
        else:
            return obj


# noinspection PyAbstractClass
class XmlSerializer(Serializer):
    """
    Xml serializer not currently implemented
    """
    pass


"""
class SerializationHandler(ABC):
    instances = None

    def __init__(self, instance):
        self.instance = instance

    def serialize(self):
        self._validate_instance()
        return self._handle()

    @abstractmethod
    def _handle(self):
        raise NotImplemented("Subclasses must implement this method")

    def _validate_instance(self):
        if not isinstance(self.instance, self.__class__.instances):
            raise InvalidObjectClassException("Invalid instance of type {}".format(self.__class__.instances))

    @staticmethod
    def get(instance):
        for class_ in SerializationHandler.__subclasses__():
            if isinstance(instance, class_.instances):
                return class_(instance)
        else:
            raise ValueError("Unknown type {}".format(instance.__class__))


class ListSerializationHandler(SerializationHandler):
    instances = list

    def _handle(self):
        raise NotImplemented("Subclasses must implement this method")


class SdkObjectSerializationHandler(SerializationHandler):
    instances = SdkObject

    def _handle(self):
        raise NotImplemented("Subclasses must implement this method")


class SdkCollectionSerializationHandler(SerializationHandler):
    instances = SdkCollectionObject

    def _handle(self):
        raise NotImplemented("Subclasses must implement this method")


class DictSerializationHandler(SerializationHandler):
    intances = dict

    def _handle(self):
        raise NotImplemented("Subclasses must implement this method")

"""
