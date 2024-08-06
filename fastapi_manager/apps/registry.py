from importlib import import_module
from importlib.util import find_spec
import inspect
import threading
from typing import Self
from fastapi_manager.db import BaseTable

from fastapi_manager.conf import settings


def module_has_submodule(package, module_name):
    """
    Copy of django's module_has_submodule function. Pasted here to avoid dependency on Django.
    :param package:
    :param module_name:
    :return:
    """
    try:
        package_name = package.__name__
        package_path = package.__path__
    except AttributeError:
        # package isn't a package.
        return False

    full_module_name = package_name + "." + module_name
    try:
        return find_spec(full_module_name, package_path) is not None
    except (ImportError, AttributeError):
        return False


class PoolInterface(object):

    def get(self, class_id):
        """
        Returns class of specified ID. Fails silently by returning None or default
        class (if supported)
        :param class_id:
        :return:
        """
        raise NotADirectoryError()

    def __getitem__(self, class_id):
        """
        Returns class of specified ID. Should throw KeyError if class of given ID
        does not exist. Never returns default class, this function should returns only
        explicitly registered classes.
        :param class_id:
        :return:
        """
        raise NotADirectoryError()

    def __contains__(self, class_id):
        """
        Check if pool has registered class of given ID.
        :param class_id:
        :return:
        """
        raise NotADirectoryError()

    def __iter__(self):
        """
        Iterates over list of tuples (class_id, class)
        :return:
        """
        raise NotADirectoryError()


class PoolRegistrationError(Exception):
    pass


class SkipRegistration(Exception):
    pass


class Signal(object):

    def __init__(self):
        self._handlers = []

    def add_handler(self, callback):
        self._handlers.append(callback)

    def __call__(self, *args, **kwargs):
        for handler in self._handlers:
            handler(*args, **kwargs)


class Pool(PoolInterface):
    """
    Pool is a manager for classes declared in various places which should be
    grouped into one pool of tools. For example, tags may be declared in multiple
    applications but should be easily accessible from one place.
    To achieve this, each tag should be registered in tag pool.

    Pool is a tool which scans all applications and looks for certain module inside
    and import them on first pool access. Each imported module can register
    classes in the pool, using pool.register() function. Registered classes
    do not have to be declared in imported module. Pool is not collecting classes,
    pool only imports some modules from each application and these modules register
    classes in the pool.

    Each class in the pool is identified by class id which is generated
    using get_class_id function. Registered classes are accessible using this ID.

    Design of this approach base on Django admin pages pool.
    """

    __shared_state = {"lock": threading.Lock(), "counter": 0}

    _registry = {}

    module_lookup = None  # leave None to avoid modules discovering and auto-loading
    base_class = None  # no base class
    default = None
    abstract = False  # is registration of abstract classes allowed?
    all_models = {}

    @classmethod
    def new(
        cls, base_class=None, module_lookup=None, default=None, abstract=False
    ) -> Self:
        """
        Returns new pool for given base
        :return:
        """
        if base_class not in cls._registry:

            cls.__shared_state["counter"] += 1
            pool_cls = type(
                "Pool{}".format(cls.__shared_state["counter"]),
                (cls,),
                {
                    "module_lookup": module_lookup,
                    "default": default,
                    "abstract": abstract,
                    "base_class": base_class,
                },
            )

            pool_id = pool_cls.get_pool_id()
            if pool_id is not None:
                if pool_id in cls._registry:
                    raise ValueError("Pool id = '{}' is already in use".format(pool_id))

                cls._registry[base_class] = pool_cls

        return cls._registry[base_class]()

    @classmethod
    def of(cls, base_class):
        # get pool of classes from given base class, works only
        return cls._registry[base_class]()

    def __init__(self):
        # To take power of shared_state and data sharing between threads
        # each class has to be unique pool. Because of that all params
        # (module_lookup, base_class, default) are class attributes and
        # should be overridden in derived pools instead of be passed
        # in init()

        # By the same reason, __init__ takes no arguments to avoid situation when
        # programmer try to instantiate same pool multiple times with different
        # arguments.

        # this lock is probably not required, but I left it to be on the safe side
        with self.__shared_state["lock"]:
            if self.__class__.__name__ not in self.__shared_state:
                self.__shared_state[self.__class__.__name__] = dict(
                    loaded=self.module_lookup is None,
                    handled=set(),
                    _errors=[],
                    _classes={},
                    _metas={},
                    module_lookup=self.module_lookup,
                    base_class=self.base_class,
                    default=self.default,
                    abstract=self.abstract,
                    # signals
                    on_register=Signal(),
                )

            self.__dict__ = self.__shared_state[self.__class__.__name__]

        self.postponed = []

    def __deepcopy__(self, memo):
        """
        Customized deepcopy which assignees same dict
        :param memo:
        :return:
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        result.__dict__ = self.__dict__
        return result

    @classmethod
    def get_pool_id(cls):
        """
        Using this ID pool can be retrieved by of() method.
        If None is returned, pool won't be available in of(). ID conflict raises ValueError exception.
        :return:
        """
        return cls.base_class

    def populate(self, packages):
        """
        Fill in all the cache information. This method is threadsafe, in the
        sense that every caller will see the same state upon return, and if the
        cache is already initialised, it does no work.
        """

        if self.loaded or self.module_lookup is None:
            return

        # Note that we want to use the import lock here - the app loading is
        # in many cases initiated implicitly by importing, and thus it is
        # possible to end up in deadlock when one thread initiates loading
        # without holding the importer lock and another thread then tries to
        # import something which also launches the app loading. For details of
        # this situation see Django #18251 issue.
        self._errors = []

        if self.loaded:
            return
        for app_name in packages:
            if app_name in self.handled:
                continue
            self.load_app(app_name, True)

        for app_name in self.postponed:
            self.load_app(app_name)

        if self._errors:
            raise Exception(str(self._errors))

        self.loaded = True
        self.post_population()

    def post_population(self):
        pass

    def load_app(self, app_name, can_postpone=False):
        """
        Loads the app with the provided fully qualified name, and returns the
        model module.
        """

        self.handled.add(app_name)
        package_name = ".".join((app_name,) + tuple(self.module_lookup.split(".")[:-1]))
        module_lookup = self.module_lookup.split(".")[-1]

        package_name = (
            f"{settings.BASE_DIR.name}.{settings.MODULES_DIR.name}.{package_name}"
        )

        try:
            package = import_module(package_name)

        except ImportError:
            # there is no such package, skip application
            raise Exception(
                f"There are no module {package_name}, please check INSTALLED_APPS in settings"
            )
            return None

        if not module_has_submodule(package, module_lookup):
            return None

        try:
            mod = import_module("%s.%s" % (package_name, module_lookup))

        except ImportError:

            if can_postpone:
                self.postponed.append(app_name)
            else:
                raise
        else:
            for name, obj in inspect.getmembers(mod):
                if inspect.isclass(obj):
                    self.register(obj, silently=True)

        # part 2: load models
        self.load_models(package_name, app_name)

    def load_models(self, package_name, app_name):
        try:
            mod = import_module("%s.%s" % (package_name, "models"))
        except ImportError:
            raise Exception(f"You need create models.py file inside {app_name} app")
        classes = inspect.getmembers(mod, inspect.isclass)

        models_list = []
        for name, model in classes:
            if issubclass(model, BaseTable) and not model is BaseTable:
                models_list.append(model)
        if len(models_list) > 0:
            self.all_models.update({app_name: models_list})

    def get_class_id(self, cls):
        return cls.__name__

    def register(self, cls=None, forced_id=None, silently=False):
        """
        Registers given class in the pool.
        Can be also used as a decorator.

        Examples:
        pool.register(FooClass)

        @pool.register
        class FooClass():
            pass

        @pool.register()
        class FooClass():
            pass

        @pool.register(silently=True):
        class FooClass():
            pass

        :param cls: Class to register
        :param forced_id: Override ID generated by the pool
        :param silently: Fails silently?
        :return:
        """

        is_decorator = cls is None

        def _decorator(dcls):
            try:
                cid, error = self._register(dcls, forced_id)
            except SkipRegistration:
                return dcls

            if error is not None and not silently:
                raise PoolRegistrationError(error)

            return dcls

        if is_decorator:
            # used as decorator
            return _decorator

        return _decorator(cls)

    def _register(self, cls, forced_id=None):

        if self.base_class is not None and not issubclass(cls, self.base_class):
            return (
                None,
                "<{}> is not a subclass of <{}> which is required by <{}> pool".format(
                    repr(cls), repr(self.base_class), repr(self)
                ),
            )

        if not self.abstract and self.is_abstract(cls):
            return (
                None,
                "Abstract class <{}> cannot be registered in <%s> pool".format(
                    repr(cls), repr(self)
                ),
            )

        cid = forced_id if forced_id is not None else self.get_class_id(cls)
        if cid is None:
            return None, "Class ID cannot be determined for <{}>".format(repr(cls))

        self.on_register(cid, cls)
        self._classes[cid] = cls

        pools = getattr(cls, "pools", set())
        pools.add(self)
        setattr(cls, "pools", pools)

        return cid, None

    def is_abstract(self, cls):
        return inspect.isabstract(cls)

    @property
    def classes(self):
        return self._classes

    def get(self, class_id):
        """
        Returns class of given ID, if there is no class of requested ID registered returns
        base class if use_base_class_as_default is set or None.
        :param class_id:
        :return:
        """
        try:
            return self[class_id]
        except KeyError:
            return (
                self.default(class_id)
                if callable(self.default) and not isinstance(self.default, type)
                else self.default
            )

    def __getitem__(self, class_id):
        """
        Returns class of requested ID. If certain class is not registered raises KeyError
        exception, even if use_base_class_as_default is set.
        :param class_id:
        :return:
        """
        return self.classes[class_id]

    def __contains__(self, class_id):
        """
        Check if class of given ID is explicitly registered. If class is not registered
        it cannot be retrieved by item getter, however valid class (base class) can be returned
        by get() method if use_base_class_as_default is set.
        :param class_id:
        :return:
        """
        return class_id in self.classes

    def __iter__(self):
        return iter(self.classes.items())

    def __eq__(self, other):
        # all instances shares same attributes, so testing classes is enough
        return self.__class__ == other.__class__

    def __hash__(self):
        return hash(self.__class__)

    def __repr__(self):
        return "{}<{}>".format(
            self.__class__.__name__,
            self.base_class.__name__ if self.base_class is not None else "ALL",
        )

    def get_models(self):
        return self.all_models

    def get_app_models(self, app_name):
        return self.all_models.get(app_name)

    def get_model(self, name):
        filtered = filter(
            lambda x: x.__table_name__ == name or x.__name__ == name, self.get_models()
        )

        vals = list(filtered)
        if len(vals) <= 0:
            raise Exception(f"Model {name} does not exist")
        return vals.pop()


class Apps(Pool):
    module_lookup = "apps"

    def __iter__(self):
        return iter(self._registry[0])

    def get_apps_list(self):
        return list(self.__iter__())

    def get_class_id(self, cls):
        try:
            return cls.name
        except Exception:
            raise Exception("You need specify name for app")


apps = Apps()
