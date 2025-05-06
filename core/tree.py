import uuid
import json
from datetime import date

class Tree:
    def __init__(self):
        self.root = Node('root')

    def print_tree(self, node = None):
        node = self.root if not node else node
        indent = " " * node.get_level() * 3
        print(indent + node.name)
        for child in node.children:
            self.print_tree(child)

    @classmethod
    def from_json(cls, filename):

        # JSON decoder sends dict to object_hook func and uses result of custom func as object
        def _object_hook(dct):
            if 'date' in dct:
                dct['date'] = date.fromisoformat(dct['date']) # Reconstruct date object from string
            return dct

        with open(filename) as f:
            data = json.load(f, object_hook=_object_hook)

        # keep all nodes in dict for later reference
        node_map = {}

        def _build_node(node_data):

            if node_data['id'] in node_map:
                raise ValueError(f"Duplicate node ID: {node_data['name']}")

            # get all non-special attributes and put in dict
            kwargs = {k: v for k, v in node_data.items() if k not in ['id', 'node_type', 'name', 'children', 'parent_id']}

            # create nodes with correct subclass
            if node_data['node_type'] == 'Route':
                node = Route(name=node_data['name'], **kwargs)
            elif node_data['node_type'] == 'Location':
                node = Location(name = node_data['name'], **kwargs)
            elif node_data['node_type'] == 'Ascent':
                node = Ascent(name = node_data['name'], **kwargs)
            else:  # if node doesn't have subclass create a generic node object NOTE: generic nodes shouldn't exist
                node = Node(name=node_data['name'], **kwargs)
            
            node.id = node_data['id'] # overwrite id that got auto generated on creation with id form json file
            node_map[node.id] = node # add node in node_map dict at key of "node_id"

            # Rebuild children recursively
            for child_data in node_data.get('children', []):
                child = _build_node(child_data)
                child.parent = node # use parent setter to reconstruct parent/child relationship

            return node

        # __new__ creates uninitialized instance of Tree() withouth calling __init__ constructor (don't create new root)
        tree = cls.__new__(cls) 
        # construct root from first node in JSON
        tree.root = _build_node(data)
        return tree

    def to_json(self, filename):
        def node_to_dict(node):
            return {
                    **node.to_dict(),
                    'children': [node_to_dict(child) for child in node.children]
                    }
        with open(filename, 'w') as f:
            json.dump(node_to_dict(self.root), f, indent=2)

    def find_node(self, name):
        if self.root is None:
            return None

        # depth-first-search
        def _dfs_recursive(node):
            if node.name == name:
                return node
            for child in node.children:
                found_node = _dfs_recursive(child)
                if found_node:
                    return found_node
            return None
        return _dfs_recursive(self.root)

    def find_route(self, name):
        node = self.find_node(name)
        if not isinstance(node, Route):
            raise ValueError(f"Node '{name}' is not a Route")
        return node

    def find_location(self, name):
        node = self.find_node(name)
        if not isinstance(node, Location):
            raise ValueError(f"Node '{name}' is not a Location")
        return node

    def add_route(self, name, parent, **kwargs):
        if parent is None:
            raise ValueError("Parent node not found")
        Route(name, parent, **kwargs)

    def add_location(self, name, parent, **kwargs):
        if parent is None:
            raise ValueError("Parent node not found")
        Location(name, parent, **kwargs)

    def delete_node(self, node):
        if node is not None:
            for child in node.children:
                self.delete_node(child)
            node.parent = None
            node.children = []

class Node:
    def __init__(self, name):
        self.name = name
        self.id = str(uuid.uuid4())
        self.children = []
        self._parent = None
        self._parent_id = None
        self._depth = 0
        self._is_expanded = True


    @property
    def parent(self):
        return self._parent

    @property
    def is_expanded(self):
        return self._is_expanded

    def toggle(self):
        self._is_expanded = not self._is_expanded

    @property
    def depth(self):
        return self.get_level()
    
    @parent.setter
    def parent(self, parent):
        if parent is self:
            raise ValueError("Cannotbe parent of itself")
        if parent and self in parent.children:
            raise ValueError("Circular reference detected")
        if self._parent:
            self._parent.children.remove(self)

        self._parent = parent

        if parent and self not in parent.children:
            parent.children.append(self)

    def to_dict(self):
        return {
                'name': self.name,
                'id': str(self.id),
                'parent_id': str(self.parent.id) if self.parent else None,
                'node_type': self.__class__.__name__,
                **{k:v for k,v in self.__dict__.items() if not k.startswith('_') and k not in ['parent', 'children']}
                }

    def get_level(self):
        level = 0
        p = self.parent
        while p: # when p = root, returns 'None' (breaking out of loop)
            level += 1
            p = p.parent
        return level

class Location(Node):
    # sun, coords?, google maps link?
    def __init__(self, name, parent=None, **kwargs):
        super().__init__(name)
        self.parent = parent
        self.coords = kwargs.get('coords', None)

class Route(Node):
    # name, grade, type, coords, image, link
    def __init__(self, name, parent=None, **kwargs):
        super().__init__(name)
        self.parent = parent
        # dict: get(key, default) gets the value at a specific key else returns default
        self.grade = kwargs.get('grade', '?')
        self.type = kwargs.get('type', None)
        self.comments = kwargs.get('comments', [])
        self.betas = kwargs.get('betas', [])


    def add_comment(self, comment):
        if not hasattr(self, 'comments'):
            raise AttributeError('Only Route nodes support comments')
        self.comments.append(comment)

    def add_beta(self, beta):
        self.betas.append(beta)
    
    def add_ascent(self, **kwargs):
        Ascent(self, **kwargs)
        

class Ascent(Node):
    # type (flash, ...), FA (bool), date, comment, video
    def __init__(self, route = None, **kwargs):
        name = f"ascent_{uuid.uuid4().hex[:8]}" 
        super().__init__(name)
        self.parent = route
        self._date = kwargs.get('date', date.today())
        self.tries = kwargs.get('tries', 'flash')
        self.first_ascent = kwargs.get('firs_ascent', False)

    @property
    def date(self):
        return self._date

    def to_dict(self):
        return {
                **super().to_dict(),
                'date': self._date.isoformat(), # convert date object to string
                }

    @classmethod
    def from_dict(cls, data):
        ascent = cls.__new__(cls)
        ascent._date = date.fromisoformat(data['date']) # reconstruct date
        return ascent

