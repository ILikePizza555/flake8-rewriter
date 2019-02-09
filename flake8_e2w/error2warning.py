from flake8.formatting import default


class RewriteFormatter(default.Default):
    error_format = "%(path)s:%(row)d:%(col)d: %(code)s %(text)s"

    def __init__(self, options):
        super().__init__(options)

        self.replacements = dict()
        for k, v in map(lambda s: s.split(":", 1), options.replacements):
            self.replacements[k] = v
    
    def add_options(self, option_manager):
        option_manager.add_option("--replace", action="append", dest="replacements", help="Given <code1>:<code2>, replaces all isntances of <code1> with <code2>.")
    
    def format(self, error):
        error.code = self.replacements.get(error.code, error.code)
        super().format(error)