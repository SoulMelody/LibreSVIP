from construct import Construct


def singleton(arg: type[Construct]) -> Construct:
    return arg()
