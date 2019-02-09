from flake8.formatting import default
from flake8.style_guide import Violation


def add_options(option_manager):
        option_manager.add_option("--replace", action="append", dest="replacements", help="Given <code1>:<code2>, replaces all isntances of <code1> with <code2>.")


def rewrite_violation(violation, new_code):
    return Violation(
        new_code,
        violation.filename,
        violation.line_number,
        violation.column_number,
        violation.text,
        violation.physical_line)


class RewriteFormatter(default.Default):
    error_format = "%(path)s:%(row)d:%(col)d: %(code)s %(text)s"

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