import weakref
# pylint: disable=trailing-whitespace
class UidSystem:
    """A UidSystem is used to manage unique identifies
        assigned to all objects of a class. 
        Usage: Create instance of UidSystem as class 
        variable in Uid tracked class. 
        Call self.instance.create(self) in tracked class 
        constructor. Each instance of tracked class has 
        a uid instance variable.
    """
    def __init__(self):
        self._objects = {}
        self._last_uid = -1

    def _next_uid(self) -> None:
        self._last_uid += 1
        return self._last_uid

    def _add(self, new) -> None:
        if new.uid in self._objects:
            raise ValueError(
                f'object with uid "{new.uid}" '
                f'already exists in system')
        self._objects[new.uid] = weakref.ref(new)

    def create(self, new) -> None:
        new.uid = self._next_uid()
        self._add(new)

    def reset(self):
        self._objects = {}
        self._last_uid = -1

    def get_by_uid(self, uid) -> object or None :
        return self._objects.get(uid)

    def get_uids(self):
        return list(self._objects.keys())
