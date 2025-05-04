from kivy.lang import Builder
from kivy.properties import BooleanProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp


class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = [{'text': str(x)} for x in range(100)]

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    ''' Adds selection and focus behavior to the view'''

class SelectableLabel(RecycleDataViewBehavior, Label):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    
    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(rv, index, data)

    # def on_touch_down(self, touch):
    #     return super().on_touch_down(touch)

    def on_touch_down(self, touch):
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        if is_selected:
            print("selection change to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))


class HomeScreen(Screen):
    pass

class RouteScreen(Screen):
    pass

class StatScreen(Screen):
    pass

class RouteApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"

        # Builder.load_file('ui/main.kv')
        Builder.load_file('ui/screens/home.kv')
        Builder.load_file('ui/screens/stat.kv')

        return Builder.load_file('ui/main.kv')

        # sm = ScreenManager()
        # sm.add_widget(HomeScreen(name='home'))
        # sm.add_widget(RouteScreen(name='route'))
        # sm.add_widget(StatScreen(name='stats'))

        # root = Builder.load_file('ui/main.kv')
        # root.ids.screen_manager
    
    def on_switch_tabs(self, bar, item, icon, name, direction=None):
        if self.root:
            self.root.ids.screen_manager.transition.direction = item.direction
            self.root.ids.screen_manager.current = name
            self.root.ids.toolbar.text = name.capitalize() if name != "home" else "Rocdoc"
            # if name == "stats":
            #     self.root.ids.toolbar.text = name.capitalize()
            # else: self.root.ids.toolbar.text = "Rocdoc"
