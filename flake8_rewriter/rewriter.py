from flake8.formatting import default
from flake8.style_guide import Violation


ENTRY_POINT_NAME = "rewriter"


class FakeStr(str):
    """
    Class that acts like a string, but .append adds to an inner list.
    This allows this plugin to record changes to options, but "trick" flake8 into 
    using rewrite as the formatter.
    """
    def __new__(cls, value):
        obj = super(FakeStr, cls).__new__(cls, value)
        obj.appended = []
        return obj

    def append(self, str):
        self.appended.append(str)


def format_option_callback(option, opt_str, value, parser, *args, **kwargs):
    if hasattr(parser.values, "format"):
        parser.values.append(value)
    else:
        v = FakeStr(ENTRY_POINT_NAME)

        if value != ENTRY_POINT_NAME:
            v.append(value)

        setattr(parser.values, "format", v)

def pop_option(option_manager, option_name):
    option_manager.parser.remove_option(option_name)

    manager_opt = filter(lambda x: x.short_option_name == option_name or x.long_option_name == option_name, option_manager.options)
    for opt in manager_opt:
        option_manager.options.remove(opt)
    
    return manager_opt

def add_options(option_manager):
    option_manager.add_option(
        "--replace",
        action="append",
        dest="replacements",
        help="Given <code1>:<code2>, replaces all instances of <code1> with <code2>.")

    # Jury-rig the option_manager
    pop_option(option_manager, "format")
    option_manager.add_option(
        "--format",
        action="callback",
        dest="format",
        callback=format_option_callback,
        help="Format errors according to the chosen formatter. (jury-rigged)"
    )

def rewrite_violation(violation, new_code):
    return Violation(
        new_code,
        violation.filename,
        violation.line_number,
        violation.column_number,
        violation.text,
        violation.physical_line)


class RewriteFormatter(default.SimpleFormatter):
    error_format = "%(path)s:%(row)d:%(col)d: %(code)s %(text)s"
    add_options = add_options

    def __init__(self, options):
        super().__init__(options)

        self.replacements = dict()
        if hasattr(options, "replacements"):
            for k, v in map(lambda s: s.split(":", 1), options.replacements):
                self.replacements[k] = v
    
    def format(self, error):
        if error.code in self.replacements:
            error = rewrite_violation(error, self.replacements[error.code])

        return super().format(error)