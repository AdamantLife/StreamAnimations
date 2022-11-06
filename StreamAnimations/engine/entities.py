from argparse import Action
from StreamAnimations import sprite

class Entity():
    def __init__(self, id: int, *, categories: list = None)-> None:
        self.id = id
        if categories is None: categories = list()
        self.categories = list(categories)

class ActionEntity(Entity):
    def __init__(self, id: int, *, categories: list = None, action = None) -> None:
        super().__init__(id, categories=categories)
        self.current_action = action

    def get_action(self):
        return self.current_action

class PriorityAI(ActionEntity):
    ## A list of tuples of (heuristic_algo, and action)
    def __init__(self, id: int, *, priority_queue = None, categories: list = None) -> None:
        super().__init__(id, categories=categories)
        if priority_queue is None: priority_queue = list()
        self.priority_queue = list(priority_queue)

    def get_action(self):
        action = super().get_action()
        if not action:
            action = self.determine_new_action()
        return action 

    def determine_new_action(self):
        return max(self.priority_queue, key=lambda hk: hk[0]())[1]