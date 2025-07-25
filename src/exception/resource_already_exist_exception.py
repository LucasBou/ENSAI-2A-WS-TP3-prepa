class ResourceAlreadyExistException(Exception):
    def __init__(self, ressource):
        self.ressource = ressource

    def __str__(self):
        return f'{self.ressource.name} already exists'