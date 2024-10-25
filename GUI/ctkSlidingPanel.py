
import customtkinter as ctk

class LateralSlidePanel(ctk.CTkFrame):

    def __init__(self, parent, start_pos, end_pos, y=0, panel_height= 1, invert=False):
        super().__init__(master = parent, bg_color='black', fg_color='black')

        #general attributes
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.width = abs(start_pos - end_pos)
        self.y = y
        self.panel_height = panel_height

        #animation logic
        self.pos = self.start_pos
        self.in_start_pos = True
        self.invert = invert

        #layout
        self.place(relx = self.start_pos, rely = self.y, relwidth = self.width, relheight = self.panel_height)

    def animate(self):
        if self.in_start_pos:
            self.animate_forward()
        else:
            self.animate_backward()

    def animate_forward(self):
        if self.pos > self.end_pos and self.invert ==False:
            self.pos -= 0.008
            self.place(relx = self.pos, rely = self.y, relwidth = self.width, relheight = self.panel_height)
            self.after(10, self.animate_forward)
        elif self.pos < self.end_pos and self.invert ==True:
            self.pos += 0.008
            self.place(relx=self.pos, rely=self.y, relwidth=self.width, relheight=self.panel_height)
            self.after(10, self.animate_forward)
        else:
            self.in_start_pos = False

    def animate_backward(self):
        if self.pos < self.start_pos and self.invert ==False:
            self.pos += 0.008
            self.place(relx = self.pos, rely = self.y, relwidth = self.width, relheight = self.panel_height)
            self.after(10, self.animate_backward)
        elif self.pos > self.start_pos and self.invert ==True:
            self.pos -= 0.008
            self.place(relx=self.pos, rely=self.y, relwidth=self.width, relheight=self.panel_height)
            self.after(10, self.animate_backward)
        else:
            self.in_start_pos = True

class VerticalSlidePanel(ctk.CTkFrame):

    def __init__(self, parent, start_pos, end_pos, start_x=0, panel_width= 1, invert=False):
        super().__init__(master = parent, bg_color='black', fg_color='black')

        #general attributes
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.height = abs(start_pos - end_pos)
        self.x = start_x
        self.panel_width = panel_width

        #animation logic
        self.pos = self.start_pos
        self.in_start_pos = True
        self.invert = invert

        #layout
        self.place(rely = self.start_pos, relx = self.x, relheight = self.height, relwidth = self.panel_width)

    def animate(self):
        if self.in_start_pos:
            self.animate_forward()
        else:
            self.animate_backward()

    def animate_forward(self):
        if self.pos > self.end_pos and self.invert ==False:
            self.pos -= 0.008
            self.place(rely = self.pos, relx = self.x, relheight = self.height, relwidth = self.panel_width)
            self.after(10, self.animate_forward)
        elif self.pos < self.end_pos and self.invert ==True:
            self.pos += 0.008
            self.place(rely = self.pos, relx = self.x, relheight = self.height, relwidth = self.panel_width)
            self.after(10, self.animate_forward)
        else:
            self.in_start_pos = False

    def animate_backward(self):
        if self.pos < self.start_pos and self.invert ==False:
            self.pos += 0.008
            self.place(rely = self.pos, relx = self.x, relheight = self.height, relwidth = self.panel_width)
            self.after(10, self.animate_backward)
        elif self.pos > self.start_pos and self.invert ==True:
            self.pos -= 0.008
            self.place(rely = self.pos, relx = self.x, relheight = self.height, relwidth = self.panel_width)
            self.after(10, self.animate_backward)
        else:
            self.in_start_pos = True