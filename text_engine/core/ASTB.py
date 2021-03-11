class ASTB:
    """
        ASTB (Abstract Syntax Tree Builder)
        give it the classes you want to use when building the ast
        then, call the instance with the ast as argument
        if the ast is a valid one, it will return the corresponding nested object
    """

    def __init__(self, *classes):
        self.classes = dict((cls.__name__, cls) for cls in classes)

    def __call__(self, ast):
        if isinstance(ast, dict):
            cls = self.classes.get(ast.get("__class__"))
            if cls is None:
                return dict((key, self(val)) for key, val in ast.items())
            else:
                if "*" in ast:
                    if isinstance(ast["*"], list):
                        args = [self(val) for val in ast["*"]]
                    else:
                        args = [self(ast["*"])]
                else:
                    args = []
                kwargs = dict((key, self(val)) for key, val in ast.items() if key not in ("__class__", "*"))
                return cls(*args, **kwargs)
        elif isinstance(ast, list):
            return [self(item) for item in ast]
        else:
            return ast
