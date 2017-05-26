from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError



api_client = SWAPIClient()


class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """
        # setattr(self, key, value) self.key = value
        for key, value in json_data.items():
            setattr(self, key, value)

    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        func = getattr(api_client, "get_{}".format(cls.RESOURCE_NAME))
        json_data = func(resource_id)
        return BaseModel(json_data)

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        if cls.RESOURCE_NAME == 'people':
            return PeopleQuerySet()
        elif cls.RESOURCE_NAME == 'films':
            return FilmsQuerySet()


class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        return 'Person: {0}'.format(self.name)


class Films(BaseModel):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):

    def __init__(self):
       # self.page = 0
        self.counter = 0
        self.objects = []
        self._count = None
        self.page_counter = 1

    def __iter__(self):
        return self.__class__()
        #could also return self

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        while True:
            if self.counter + 1 > len(self.objects):
                try:
                    self._get_next_page()
                except SWAPIClientError:
                    raise StopIteration()
            elem = self.objects[self.counter]
            self.counter += 1
            return elem


    def _get_next_page(self):
    #get_RESOURCENAME_pagenum
    #getattr(api_client, "get_{}".format(self.RESOURCE_NAME))(page=self.page_counter)
    #/people?page=2

        next_page = getattr(api_client, "get_{}".format(self.RESOURCE_NAME))(page=self.page_counter)
        Model = eval(self.RESOURCE_NAME.title())
        for item in next_page['results']:
            self.objects.append(Model(item))

        self._count = next_page['count']

        self.page_counter += 1

        #for item in next_page['results']:


    next = __next__

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
    #if not qs.attr:
        #request API to get it and return it
    #return qs.attr
        if not self._count:
            self._get_next_page()
        return self._count


class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self):
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))
