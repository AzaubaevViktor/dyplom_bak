import os


class MetaEnv(type):
    _cache = {}

    @classmethod
    def clear_cache(mcs):
        mcs._cache = {}

    @classmethod
    def __getattr__(mcs, item):
        if item not in mcs._cache:
            mcs._cache[item] = os.environ[item]
            try:
                mcs._cache[item] = int(mcs._cache[item])
            except ValueError:
                pass

        return mcs._cache[item]


class Env(object, metaclass=MetaEnv):
    pass


if '__main__' == __name__:
    print(Env.PYTHONUNBUFFERED)
    assert Env.PYTHONUNBUFFERED == 1
    Env.clear_cache()
    assert Env.PYTHONUNBUFFERED == 1
