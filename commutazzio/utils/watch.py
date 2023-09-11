import time
import logging

def timeit(method):
    """
    https://medium.com/pythonhive/python-decorator-to-measure-the-execution-time-of-methods-fa04cb6bb36d
    """
    def wrapper(*args, **kw):
        logging.debug(f"Entering function {method.__name__}")
        start_time = time.time()
        result = method(*args, **kw)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.debug(f"Function {method.__name__} finished in {elapsed_time:.2f} seconds")
        # te = time.time()
        # if 'log_time' in kw:
        #     name = kw.get('log_name', method.__name__.upper())
        #     kw['log_time'][name] = int((te - ts) * 1000)
        # else:
        #     # print('%r  %2.2f ms' % \
        #     #       (method.__name__, (te - ts) * 1000))
        #     print('%r  %2.2f s' % \
        #           (method.__name__, (te - ts)))
        return result
    return wrapper