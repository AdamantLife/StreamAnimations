from StreamAnimations import sprite


class Entity():
    def __init__(self, id: int, categories: list = None)-> None:
        self.id = id
        self.categories = list(categories)


class SpriteEntity(Entity):
    def __init__(self, id, sprite):
        super().__init__(id)
        self.sprite = sprite    