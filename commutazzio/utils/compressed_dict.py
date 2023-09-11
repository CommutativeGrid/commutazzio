import lz4.frame
compress = lambda x: lz4.frame.compress(x, compression_level=3)
decompress = lz4.frame.decompress
# from zlib import compress, decompress
from multiprocessing import Pool
MIN_COMPRESS_LENGTH = 9999

class CompressedDict(dict):
    _exposed_ = ['__setitem__','__getitem__', '__contains__', '__delitem__','keys','values','items']
    
    def _parallel_init(self, kv_pair):
        # print(f"Compressing key:{k}")
        k, v = kv_pair
        return {k: self._compress(v)}

    def __init__(self, data=None):
            super().__init__()  # Initialize the underlying dictionary
            if data:
                if isinstance(data, dict):
                    with Pool(processes=8) as pool:
                        results = pool.map(self._parallel_init, data.items())
                    for r in results:
                        super().update(r)
                elif isinstance(data, CompressedDict):
                    super().__init__(data)
    
    # @property
    # def count(self):
    #     if not hasattr(self, '_count'):
    #         self._count = 0
    #     return self._count

    # @count.setter
    # def count(self, value):
    #     self._count = value

    # def __init__(self, data=None):
    #     super().__init__()  # Initialize the underlying dictionary
    #     self._count=0
    #     if data:
    #         if isinstance(data, CompressedDict) or isinstance(data, dict):
    #             for k, v in data.items():
    #                 self[k] = v  # This will invoke the overridden __setitem__ method

    @staticmethod
    def _compress(value):
        text, length = value
        # only compress if it's worth it
        # do not double compress
        if not isinstance(text, bytes) and length > MIN_COMPRESS_LENGTH:
            compressed_value = (compress(text.encode()), length)
        else:
            compressed_value = (text, length)
        return compressed_value

    def __setitem__(self, key, value):
        super().__setitem__(key, self._compress(value))

    def __getitem__(self, key):
        compressed_value, length = super().__getitem__(key)
        if isinstance(compressed_value, bytes):
            return decompress(compressed_value).decode(), length
        else:
            return compressed_value, length
        
from multiprocessing.managers import BaseManager
class CompressedDictManager(BaseManager):
    pass
CompressedDictManager.register('CompressedDict', CompressedDict, exposed=CompressedDict._exposed_)




# class CompressedDict():
#     def __init__(self,data=None):
#         self._data = {} # underlying dictionary object
#         if isinstance(data, CompressedDict):
#             for k, v in data.items():
#                 self._data[k] = v
#         elif isinstance(data, dict):
#             for k, v in data.items():
#                 self[k] = v #calls __setitem__

#     def items(self):
#         return {(k, self[k]) for k in self._data.keys()}

#     def __setitem__(self, key, value):
#         text,length = value 
#         # only compress if it's worth it
#         # do not double compress
#         if not isinstance(text, bytes) and length > 999:
#             compressed_value = (compress(text.encode()),length)
#         else:
#             compressed_value = (text,length)
#         self._data[key] = compressed_value

#     def __getitem__(self, key):
#         compressed_value,length = self._data[key]
#         if isinstance(compressed_value, bytes):
#             return decompress(compressed_value).decode(),length
#         else:
#             return compressed_value,length

#     def __delitem__(self, key):
#         del self._data[key]

#     def __contains__(self, key):
#         return key in self._data

#     def __repr__(self):
#         return str({k: self[k] for k in self._data})
    
#     def __keys__(self):
#         return self._data.keys()
    
#     def __len__(self):
#         return len(self._data)
    
# from multiprocessing.managers import NamespaceProxy

# # Proxy for CompressedDict
# class CompressedDictProxy(NamespaceProxy):
#     _exposed_ = ('__setitem__', '__getitem__', '__delitem__', '__contains__', '__repr__', '__keys__', '__len__')

#     def __setitem__(self, key, value):
#         callmethod = self._callmethod
#         return callmethod('__setitem__', (key, value))
    
#     def __getitem__(self, key):
#         callmethod = self._callmethod
#         return callmethod('__getitem__', (key,))
    
#     def __delitem__(self, key):
#         callmethod = self._callmethod
#         return callmethod('__delitem__', (key,))
    
#     def __contains__(self, key):
#         callmethod = self._callmethod
#         return callmethod('__contains__', (key,))
    
#     def __repr__(self):
#         callmethod = self._callmethod
#         return callmethod('__repr__')
    
#     def __keys__(self):
#         callmethod = self._callmethod
#         return callmethod('__keys__')
    
#     def __len__(self):
#         callmethod = self._callmethod
#         return callmethod('__len__')


# from multiprocessing.managers import BaseManager
# # Custom manager
# class SharedCompressedDictManager(BaseManager):
#     pass

# # Register the CompressedDict and its proxy with the manager
# SharedCompressedDictManager.register('CompressedDict', CompressedDict, CompressedDictProxy)
