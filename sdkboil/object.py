class SdkObject(object):
    """
    Class representing sdk objects wrapping requests/responses bodies. It can be constructed and can be serialized from/to
    dict objects. Every Subclass must define their validation schema at class level
    """
    schema = {}
    # Mapping dict between objects namespaces in the json representation and SdkObject classes
    # for every defined sub_object in this mapping the from_json method will instantiate the correct SdkObject class
    # in every other case the object will be deserialized as a dictionary
    # nested subobjects namespaces can be defined with their path in the dict separated by '.'

    sub_objects = {}

    def __init__(self, *args, **kwargs):
        """
        SdkObject.__init__ signature takes an argument for every key defined at top level in the schema dict
        """
        pass


class SdkCollectionObject(object):
    elements_class = None

    def __init__(self, collection):
        self.collection = collection

    def __iter__(self):
        return self.collection.__iter__()

    def __getitem__(self, item):
        return self.collection[item]
