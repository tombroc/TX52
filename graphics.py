#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*-iso-8859-15 -*
import os
from tkinter import *

class Application:
	def _create_circle_arc(self, x, y, r, **kwargs):
		if "start" in kwargs and "end" in kwargs:
			kwargs["extent"] = kwargs["end"] - kwargs["start"]
			del kwargs["end"]
			return self.create_arc(x-r, y-r, x+r, y+r, **kwargs)
			.Canvas.create_circle_arc = _create_circle_arc;


			def draw_radar(REAL_SCOPE, WIDTH_CANVAS, HEIGHT_CANVAS):

		# Detection zone 
		# Coordon

		VIRTUAL_SCOPE = REAL_SCOPE * WIDTH_CANVAS / WIDTH_SCALE;
		x0 = WIDTH_CANVAS / 2;
		y0 = HEIGHT_CANVAS;

		x1 = 0;
		y1 = HEIGHT_CANVAS - VIRTUAL_SCOPE;

		x=x1
		y=x;

		while x < WIDTH_CANVAS / 2:
			canvas_c.create_line(x0, y0, x1+x, y1, fill='red');
			x += 10;
			y += 10;

			while x <= WIDTH_CANVAS:
				canvas_c.create_line(x0, y0, x1+x, y1, fill='red');
				x += 10;
				y -= 10;


				def __init__(self):

		# GLOBAL VARIABLES
		# CAPTOR SCALE
		REAL_SCOPE = 200;
		
		# Width equivalency (in meters)
		WIDTH_SCALE = 400;

		# Scope at scale
		VIRTUAL_SCOPE = 0;

		# Main window
		win = Tk();
		win.title("Drones interseption");
		win.attributes('-fullscreen', 1);


		# Simulation zone
		HEIGHT = win.winfo_height();
		WIDTH = win.winfo_width();
		
		# Label title
		main_l = Label(win, text='Drones interseption simulation', font=("Purisa",12,"bold","italic"));
		main_l.grid(row=1,column=1,padx=10,pady=10);
		
		HEIGHT_CANVAS = HEIGHT*0.8;
		WIDTH_CANVAS = WIDTH*0.66;

		VIRTUAL_SCOPE = REAL_SCOPE * WIDTH_CANVAS / WIDTH_SCALE;

		canvas_c = Canvas(win, width = WIDTH_CANVAS, height = HEIGHT_CANVAS, bg ='green');
		canvas_c.grid(row=3,column=1,padx=10, pady=10);

		
		# exit button
		quit_b = Button(win,text='Quit',command=quit);
		quit_b.grid(row=3,column=3,padx=10,pady=10);

		
		# Scope scale
		
		scale_s = Scale(win,variable=REAL_SCOPE, command=draw_radar(REAL_SCOPE, WIDTH_CANVAS, HEIGHT_CANVAS));
		print(REAL_SCOPE)
		scale_s.grid(row=3,column=2);
		
		#draw_radar(VIRTUAL_SCOPE, WIDTH_CANVAS, HEIGHT_CANVAS)

		win.mainloop();
