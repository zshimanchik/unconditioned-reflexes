from World import World, distance
from AnimalInfoWindow import AnimalInfoWindow


import cairo
import random
import math
from gi.repository import Gtk, GObject


TWO_PI = 2*math.pi



class gui():
    def __init__(self):
        self.world = World(200, 200)

        self.animal_info_window = None

        builder = Gtk.Builder()
        builder.add_from_file("MainWindow.glade")
        builder.connect_signals(self)

        self.window = builder.get_object("applicationwindow1")
        self.drawing_area = builder.get_object("drawingarea1")
        self.lbl_size = builder.get_object("lbl_size")

        self.window.realize()
        self.window.set_reallocate_redraws(True)
        self.window.set_title("Animals")
        self.window.connect('delete_event', Gtk.main_quit)
        self.window.connect('destroy', lambda quit: Gtk.main_quit())

        self.scrollbar1 = builder.get_object("scrollbar1")

        self.window.show_all()

        self.timer_interval = 500
        self.timer_id = GObject.timeout_add(300, self.on_timer_event)

        self.selected_animal = None
        self.is_food_smell = False


    def on_configure(self, widget, event):
        self.world.width = widget.get_allocated_width()
        self.world.height = widget.get_allocated_height()
        return True

    def on_draw(self, widget, cr):
        #Animals
        for animal in self.world.animals:
            if animal == self.selected_animal:
                cr.set_source_rgb(1, 0.84, 0)
            else:
                cr.set_source_rgb(0.6, 0.7, 0.5)
            cr.arc(animal.x, animal.y, animal.size, 0, TWO_PI)
            cr.fill()

            cr.set_source_rgb(0,0,0)
            for x, y in animal.sensors_positions:
                cr.arc(x, y, 1, 0, TWO_PI)
                cr.fill()
            cr.move_to(animal.x, animal.y)
            cr.line_to(animal.x+math.cos(animal.angle)*animal.size,
                       animal.y+math.sin(animal.angle)*animal.size)
            cr.stroke()


        for food in self.world.food:
            cr.set_source_rgb(0.3, 0.3, 0.3)
            cr.arc(food.x, food.y, food.size, 0, TWO_PI)
            cr.fill()
            cr.arc(food.x, food.y, World.MAX_EATING_DISTANCE + food.size, 0, TWO_PI)
            cr.set_line_width(0.1)
            cr.stroke()
            if self.is_food_smell:
                r1 = cairo.RadialGradient(food.x, food.y, food.size, food.x, food.y, food.smell_size)
                r1.add_color_stop_rgba(0, 0.3, 0.6, 0.3, 0.2)
                r1.add_color_stop_rgba(1, 0.3, 0.6, 0.3, 0.01)
                cr.set_source(r1)
                cr.arc(food.x, food.y, food.smell_size, 0, TWO_PI)
                cr.fill()
        return False


    def on_timer_event(self):
        self.world.update()
        if self.animal_info_window:
            self.animal_info_window.update_graphics()
            self.animal_info_window.drawing_area.queue_draw()
        self.drawing_area.queue_draw()
        self.lbl_size.set_text("animal count=" + str(len(self.world.animals)))
        return True

    def on_scrollbar1_change_value(self, *args):
        self.timer_interval = args[2]
        if self.timer_id:
            GObject.source_remove(self.timer_id)
            self.timer_id = GObject.timeout_add(self.timer_interval, self.on_timer_event)

    def on_pause_button_clicked(self, *args):
        if self.timer_id:
            GObject.source_remove(self.timer_id)
            self.timer_id = None
        else:
            self.timer_id = GObject.timeout_add(self.timer_interval, self.on_timer_event)

    def on_food_smell_checkbox_toggled(self, check_button):
        self.is_food_smell = check_button.get_active()

    def on_menuitem1_activate(self, menuitem):
        if self.animal_info_window:
            self.animal_info_window.window.close()
        self.animal_info_window = AnimalInfoWindow(self.selected_animal)
        pos = self.window.get_position()
        self.animal_info_window.window.move(pos[0] + self.window.get_allocated_width(), pos[1])

    def on_menuitem_restart_activate(self, menuitem):
        self.world = World(200, 200)

    def on_action_group_changed(self, radiobutton):
        if radiobutton.get_active():
            print(radiobutton)

    def get_animal(self, x, y):
        for animal in self.world.animals:
            if distance(x, y, animal.x, animal.y) < animal.size:
                return animal

    def on_drawingarea1_touch_event(self, action_box, void):
        self.selected_animal = self.get_animal(void.x,void.y)
        if self.animal_info_window:
            self.animal_info_window.animal = self.selected_animal


if __name__ == '__main__':
    g = gui()
    Gtk.main()