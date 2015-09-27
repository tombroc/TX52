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


	Canvas.create_circle_arc = _create_circle_arc;

	def draw_radar(self, REAL_SCOPE, WIDTH_CANVAS, HEIGHT_CANVAS, WIDTH_SCALE, canvas_c):

		# Detection zone 
		
		# Coordonnées

		canvas_c.delete("all");
		VIRTUAL_SCOPE = REAL_SCOPE * WIDTH_CANVAS / WIDTH_SCALE;
		print(REAL_SCOPE);
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
		return canvas_c;

	def __init__(self):
		#def main(self):

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
		canvas_c.grid(row=3,column=1,rowspan=20,padx=10, pady=10);

		
		# exit button
		quit_b = Button(win,text='Quit',command=quit);
		quit_b.grid(row=6,column=2,padx=10,pady=10);

		
		# Scope scale
		scale_l = Label(win, text='Scope value :');
		scale_l.grid(row=3, column=2);
		# scale_s = Scale(win, command=Application.draw_radar(self, REAL_SCOPE, WIDTH_CANVAS, HEIGHT_CANVAS, WIDTH_SCALE, canvas_c));
		scale_s = Scale(win, from_=1, to=REAL_SCOPE*2, length=300, orient=HORIZONTAL, command=lambda canvas_c = canvas_c: self.draw_radar(scale_s.get(), WIDTH_CANVAS, HEIGHT_CANVAS, WIDTH_SCALE, canvas_c));
		scale_s.set(REAL_SCOPE);
		#print(REAL_SCOPE);
		scale_s.grid(row=4,column=2);

		getscale_b = Button(win, text="Apply new scale", command=lambda canvas_c = canvas_c: self.draw_radar(scale_s.get(), WIDTH_CANVAS, HEIGHT_CANVAS, WIDTH_SCALE, canvas_c))

		getscale_b.grid(row=5, column=2);
		self.draw_radar(scale_s.get(), WIDTH_CANVAS, HEIGHT_CANVAS, WIDTH_SCALE, canvas_c);

		win.mainloop();
