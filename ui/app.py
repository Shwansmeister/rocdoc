from kivy.app import StringProperty
from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty
from kivy.lang import Builder
from kivy.resources import resource_find
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.screen import MDScreen
from core.tree import Tree
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout

class NodeItem(MDBoxLayout):
    text = StringProperty()
    depth = NumericProperty()
    is_expanded = BooleanProperty()


class TreeRV(RecycleView):
    def refresh_view(self, root_node):
        self.data = self._flatten_tree(root_node)

    def _flatten_tree(self, node):
        visible_nodes = []
        if not node:
            return visible_nodes
        
        if node.name != 'root':
            visible_nodes.append({
                'viewclass': 'NodeItem',
                'node': node,
                'depth': node.depth,
                'text': node.name,
                'is_expanded': node.is_expanded,
            })

        if node.is_expanded:
            print(node.name)
            for child in node.children:
                visible_nodes.extend(self._flatten_tree(child))
        return visible_nodes

class HomeScreen(MDScreen):
    tree_view = ObjectProperty(None)
    # chevron = ObjectProperty(None)


    def on_enter(self):
        # print("RV exists?", hasattr(self, 'tree_view'))
        Clock.schedule_once(self.init_tree) # Delay for widget creation

    def init_tree(self, dt):
        if not hasattr(self, 'tree'):
            self.tree = Tree().from_json('data/tree.json')
            if self.tree_view:
                self.tree_view.refresh_view(self.tree.root)
            else:
                print("Error: tree_view no created!")

    def on_node_click(self, node):
        print(self.ids)
        self.ids.chevron_icon = "chevron-down"
        node.toggle()
        self.tree_view.refresh_view(self.tree.root)

class RouteScreen(Screen):
    pass

class StatScreen(Screen):
    pass

class RouteApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"

        Builder.load_file('ui/screens/home.kv')
        Builder.load_file('ui/screens/stat.kv')

        return Builder.load_file('ui/main.kv')

    def on_switch_tabs(self, bar, item, icon, name, direction=None):
        if self.root:
            self.root.ids.screen_manager.transition.direction = item.direction
            self.root.ids.screen_manager.current = name
            self.root.ids.toolbar.text = name.capitalize() if name != "home" else "Rocdoc"
