def __getattr(name):
    if name == "Cpu":
        from .models import Cpu
        return Cpu
    raise AssertionError(f"module {__name__} has no attribute {name}")