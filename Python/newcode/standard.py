"""Reserved Newcode standard modules for the Python reference runtime."""

from fractions import Fraction
from math import floor
from pathlib import PurePosixPath

from newcode.errors import Span, fail
from newcode.model import NativeRoutine
from newcode.paths import safe_file_path, safe_relative_path


STANDARD_PREFIX = "standard/"


def _params(*items):
    return [(type_name, name, Span(1, 1)) for type_name, name in items]


def _integer(value, label, span):
    if value.denominator != 1:
        raise fail("THINKLOGIC ERROR", f"{label} must be an integer", span)
    return value.numerator


def _setseed(runtime, values, span):
    runtime.random_generator.seed(_integer(values[0], "seed", span))
    return None


def _randomnumber(runtime, values, span):
    lower = _integer(values[0], "lower bound", span)
    upper = _integer(values[1], "upper bound", span)
    if lower > upper:
        raise fail("THINKLOGIC ERROR", "lower bound must not exceed upper bound", span)
    return Fraction(runtime.random_generator.randint(lower, upper))


def _randomfraction(runtime, values, span):
    return Fraction(runtime.random_generator.getrandbits(53), 1 << 53)


def _currenttime(runtime, values, span):
    now = runtime.now_provider()
    return {
        "year": Fraction(now.year),
        "month": Fraction(now.month),
        "day": Fraction(now.day),
        "hour": Fraction(now.hour),
        "minute": Fraction(now.minute),
        "second": Fraction(now.second),
    }


def _timecount(runtime, values, span):
    return Fraction(floor(runtime.time_provider()))


def _approved_path(runtime, raw, span):
    value = safe_relative_path(raw, span)
    runtime.censor.check(value, False, span)
    return value


def _joinpath(runtime, values, span):
    left = safe_relative_path(values[0], span)
    right = safe_relative_path(values[1], span)
    return _approved_path(runtime, str(PurePosixPath(left) / right), span)


def _filename(runtime, values, span):
    return _approved_path(runtime, PurePosixPath(safe_relative_path(values[0], span)).name, span)


def _extension(runtime, values, span):
    name = PurePosixPath(safe_relative_path(values[0], span)).name
    value = name.rsplit(".", 1)[1] if "." in name[1:-1] else ""
    runtime.censor.check(value, False, span)
    return value


def _parentpath(runtime, values, span):
    return _approved_path(runtime, str(PurePosixPath(safe_relative_path(values[0], span)).parent), span)


def _pathexists(runtime, values, span):
    return safe_file_path(runtime.cwd, values[0], span).is_file()


def _arguments(runtime, values, span):
    for value in runtime.command_args:
        runtime.censor.check(value, False, span)
    return list(runtime.command_args)


def _argument(runtime, values, span):
    index = _integer(values[0], "argument index", span)
    if index < 0 or index >= len(runtime.command_args):
        raise fail("INPUTCRIME", "command argument does not exist", span)
    value = runtime.command_args[index]
    runtime.censor.check(value, False, span)
    return value


def _module(routines):
    return {routine.name: routine for routine in routines}


STANDARD_MODULES = {
    "standard/randomthink.think": _module([
        NativeRoutine(Span(1, 1), "silencethink", "setseed", _params(("numberthink", "seed")), _setseed),
        NativeRoutine(Span(1, 1), "numberthink", "randomnumber", _params(("numberthink", "lower"), ("numberthink", "upper")), _randomnumber),
        NativeRoutine(Span(1, 1), "numberthink", "randomfraction", _params(), _randomfraction),
    ]),
    "standard/timethink.think": _module([
        NativeRoutine(Span(1, 1), "recordthink", "currenttime", _params(), _currenttime),
        NativeRoutine(Span(1, 1), "numberthink", "timecount", _params(), _timecount),
    ]),
    "standard/paththink.think": _module([
        NativeRoutine(Span(1, 1), "wordthink", "joinpath", _params(("wordthink", "left"), ("wordthink", "right")), _joinpath),
        NativeRoutine(Span(1, 1), "wordthink", "filename", _params(("wordthink", "path")), _filename),
        NativeRoutine(Span(1, 1), "wordthink", "extension", _params(("wordthink", "path")), _extension),
        NativeRoutine(Span(1, 1), "wordthink", "parentpath", _params(("wordthink", "path")), _parentpath),
        NativeRoutine(Span(1, 1), "goodthink", "pathexists", _params(("wordthink", "path")), _pathexists),
    ]),
    "standard/commandthink.think": _module([
        NativeRoutine(Span(1, 1), "listthink", "arguments", _params(), _arguments),
        NativeRoutine(Span(1, 1), "wordthink", "argument", _params(("numberthink", "index")), _argument),
    ]),
}


def standard_module(path):
    return STANDARD_MODULES.get(path)
