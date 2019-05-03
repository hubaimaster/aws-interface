cache_dict = {}


class Cache(dict):
    def __init__(self, partition):
        super(Cache, self).__init__()
        self.partition = partition
        dictionary = cache_dict.get(partition, {})
        self._load(dictionary)

    def __setitem__(self, key, value):
        super(Cache, self).__setitem__(key, value)
        self.save()

    def _load(self, dictionary):
        for key in dictionary:
            self[key] = dictionary[key]

    def _dump(self, dictionary):
        for key in self:
            dictionary[key] = self[key]

    def save(self):
        cache_dict[self.partition] = self
        self._dump(cache_dict)
