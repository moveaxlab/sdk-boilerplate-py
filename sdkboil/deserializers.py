import json
import inspect

from abc import ABC, abstractmethod

from .object import SdkCollectionObject, SdkObject
from .exception import MissingContentTypeException, UnknownContentTypeException
from .headers import APPLICATION_JSON, APPLICATION_FORM_URLENCODED


def _get_deserializer(content_type):
    if not content_type:
        raise MissingContentTypeException("Cannot get correct serializer without defining the Content-Type")
    elif content_type == APPLICATION_JSON:
        return JsonDeserializer
    elif content_type == APPLICATION_FORM_URLENCODED:
        return FormDeserializer
    else:
        raise UnknownContentTypeException("Unsupported Content-Type: {}".format(content_type))


class Deserializer(ABC):
    @staticmethod
    @abstractmethod
    def deserialize(class_, json_string):
        raise NotImplemented("Subclasses must implement this method")


class JsonDeserializer(object):
    @staticmethod
    def _get_init_args(class_, dict_):
        init_parameters = dict(inspect.signature(class_.__init__).parameters)
        init_args = {}
        for param in dict_:
            if param in init_parameters:
                init_args[param] = dict_[param]
        return init_args

    @staticmethod
    def deserialize(class_, json_string):
        """
        Deserializes a json_dict into an SdkObject instance. Every sub_object defined at class level will be recursively
        deserialized into instances of their class
        """
        json_data = json.loads(json_string)
        if issubclass(class_, SdkCollectionObject):
            return class_(JsonDeserializer._deserialize_array(class_.elements_class, json_data))
        elif issubclass(class_, SdkObject):
            init_args = JsonDeserializer._get_init_args(class_, JsonDeserializer._deserialize_dict(class_, json_data))
            return class_(**init_args)
        else:
            return json_data

    @staticmethod
    def _deserialize_dict(class_, dict_):
        """
        Deserializes a dict into an instance of the given class. if the class defines a sub_objects dict, correspodning
        sub_objects will be deserialized aswell
        """
        sub_objects = class_.sub_objects
        for sub_obj_namespace, sub_obj_class in sub_objects.items():
            dict_ = JsonDeserializer._deserialize_sub_object(sub_obj_namespace, sub_obj_class, dict_)
        return dict_

    @staticmethod
    def _deserialize_sub_object(namespace, class_, dict_):
        keys = namespace.split('.')
        tmp = dict_
        for key in keys[:-1]:
            dict_ = dict_[key]

        if isinstance(class_, list):
            dict_[keys[-1]] = JsonDeserializer._deserialize_array(class_[0], dict_[keys[-1]])
        else:
            dict_[keys[-1]] = JsonDeserializer._deserialize_dict(class_, dict_[keys[-1]])
        return tmp

    @staticmethod
    def _deserialize_array(elements_class, array):
        if issubclass(elements_class, SdkCollectionObject):
            return JsonDeserializer._deserialize_array(SdkCollectionObject.elements_class, array)
        elif issubclass(elements_class, SdkObject):
            return [JsonDeserializer._deserialize_dict(elements_class, el) for el in array]
        else:
            return array


class FormDeserializer(Deserializer):
    @staticmethod
    def deserialize(raw, class_):
        return class_(**raw)


# noinspection PyAbstractClass
class XmlDeserializer(Deserializer):
    """
    Xml Deserializer not yet implemented
    """
    pass
