from abc import ABCMeta, ABC, abstractmethod

from scrapy.contracts import Contract
from scrapy.exceptions import ContractFail


class MetaContract(Contract):
    """
    Contract to add a metadata pair to the request
    @meta key value
    """
    name = "meta"

    def __init__(self, method, *args):
        assert len(args) == 2, "params must be <meta name> <meta value>"
        self.key, self.value = args

    def adjust_request_args(self, args):
        if args.get("meta") is None:
            args["meta"] = {}
        args["meta"][self.key] = self.value
        return args


class ResultCheckerMeta(ABCMeta):
    def __new__(mcs, name, bases, attrs, **kwargs):
        cls = super().__new__(mcs, name, bases, attrs)
        if "result_name" in attrs:
            for b in bases:
                if hasattr(b, "_all_checkers"):
                    b._all_checkers[attrs["result_name"]] = cls()
        return cls


class SpecificResultChecker(metaclass=ResultCheckerMeta):
    """
    The base class of specific result checker
    Subclass must provide:
     - a ``result_name`` class attribute
     - a method named ``check_match`` which accept a returned item and returns bool 
        value indicates if it matches the result type
    """
    _all_checkers = {}

    @abstractmethod
    def check_match(self, output_item):
        pass

    @classmethod
    def get_checker(cls, result_name):
        return cls._all_checkers.get(result_name)


class SpecificReturnsContract(Contract):
    """
    This contract allows user to check if a specific type of result returned
    Usage: 
    @returns_specific <result type> [min=1 [max]]
    To add a result type, you need create a new class inherits SpecificResultChecker
    and make sure the module contains your subclasses is imported
    """

    name = "returns_specific"

    def __init__(self, method, *args):
        super().__init__(method, *args)
        self.result_name = args[0]
        self.checker = SpecificResultChecker.get_checker(self.result_name)
        if self.checker is None:
            raise TypeError(
                "unknown result name {},"
                "try to create a subclass of SpecificResultChecker to register a handler of this result,"
                "and make sure the module it's loaded".format(self.result_name))
        try:
            self.min_bound = int(args[1])
        except IndexError:
            self.min_bound = 1
        try:
            self.max_bound = int(args[2])
        except IndexError:
            self.max_bound = float('inf')

    def post_process(self, output):
        occurrences = 0
        for x in output:
            if self.checker.check_match(x):
                occurrences += 1

        assertion = (self.min_bound <= occurrences <= self.max_bound)

        if not assertion:
            if self.min_bound == self.max_bound:
                expected = self.min_bound
            else:
                expected = '%s..%s' % (self.min_bound, self.max_bound)

            raise ContractFail(
                "Returned {} {} requests, expected {}".
                format(occurrences, self.result_name, expected))


from . import beibei
