class NamedFile:
    def __init__(self, file, name):
        self.file = file
        self.name = name

    def read(self, *args, **kwargs):
        return self.file.read(*args, **kwargs)

    def __getattr__(self, attr):
        return getattr(self.file, attr)
