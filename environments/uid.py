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
        """Increment internal _last_uid and return it. Used 
            when generating new uniquely identified objects.

        Returns:
            int: a unique identifier
        """
        self._last_uid += 1
        return self._last_uid

    def _add(self, new) -> None:
        """Internal method for appending new object and its 
            uid to internal _objects.

        Args:
            new (object): object to append

        Raises:
            ValueError: object's uid is not unique
        """
        if new.uid in self._objects:
            raise ValueError(
                f'object with uid "{new.uid}" '
                f'already exists in system')
        self._objects[new.uid] = weakref.ref(new)

    def create(self, new) -> None:
        """Called in constructor for tracked class. Handles 
            generation of new uid and adding to UidSystem 
            _object dict.

        Args:
            new (object): object to create in UidSystem
        """
        new.uid = self._next_uid()
        self._add(new)

    def reset(self):
        """Resets system. Tracked uids and instances are lost.
        """
        self._objects = {}
        self._last_uid = -1

    def get_by_uid(self, uid) -> object or None :
        """Return object in system with uid. If not object with
            uid, return None

        Args:
            uid (int): uid to search with

        Returns:
            object: object if found else None
        """
        return self._objects.get(uid)

    def get_uids(self):
        """Returns list of tracked uids.

        Returns:
            list: tracked uids
        """
        return list(self._objects.keys())
