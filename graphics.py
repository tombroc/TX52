#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*-iso-8859-15 -*
import os
from tkinter import *
from math import sqrt
import time
import random

class Application():
	def _create_circle_arc(self, x, y, r, **kwargs):
		if "start" in kwargs and "end" in kwargs:
			kwargs["extent"] = kwargs["end"] - kwargs["start"]
			del kwargs["end"]
			return self.create_arc(x-r, y-r, x+r, y+r, **kwargs)


	Canvas.create_circle_arc = _create_circle_arc;

	def draw_radar(self, REAL_SCOPE, WIDTH_CANVAS, HEIGHT_CANVAS, HEIGHT_SCALE, CANVAS_C):

		# Detection zone 
		
		# Coordonnées

		CANVAS_C.delete("arcs");
		VIRTUAL_SCOPE = REAL_SCOPE * WIDTH_CANVAS / HEIGHT_SCALE;
	
		x0 = WIDTH_CANVAS / 2;
		y0 = HEIGHT_CANVAS;
		r = 0;

		while r < VIRTUAL_SCOPE:
			CANVAS_C.create_circle_arc(x0, y0, r, style='arc', outline="red", width=1, start=30, end=150, tags="arcs");
			r += 10;

		return CANVAS_C;
	
	def add_intruder(self, REAL_SCOPE, WIDTH_CANVAS, HEIGHT_CANVAS, HEIGHT_SCALE, CANVAS_C, warning_l, intruder_b):
		
		# To improve by using threads
		intruder_b.config(state=DISABLED);
		Y = 1;
		X = random.uniform(0, WIDTH_CANVAS);
		dX = 0;
		dY = 1;
		VIRTUAL_SCOPE = REAL_SCOPE * HEIGHT_CANVAS / HEIGHT_SCALE;

		warning_l.grid_forget();
		CANVAS_C.delete("point");
		
		intruder = CANVAS_C.create_polygon(X, Y, X+20, Y+20, X-20, Y+20, tags="point");
		
		while (Y < HEIGHT_CANVAS - VIRTUAL_SCOPE):
			Y = Y + dY;
			dX = random.uniform(-1.5, 2);
			X = X + dX;
			CANVAS_C.move(intruder,dX,dY);
			CANVAS_C.update();
			time.sleep(0.025);
		warning_l.grid(row=6, column=2);	
		intruder_b.config(state=NORMAL);

	def __init__(self):

		
		# GLOBAL VARIABLES
		#def main(self):
		# CAPTOR SCALE
		REAL_SCOPE = 200;
		
		# Width equivalency (in meters)
		HEIGHT_SCALE = 400;

		# Scope at scale
		VIRTUAL_SCOPE = 0;

		# Main window
		win = Tk();
		win.title("Drones interseption");
		win.attributes('-fullscreen', 1);
		
		# Simulation zone
		HEIGHT = win.winfo_height();
		WIDTH = win.winfo_width();
		
		warning_l = Label(win, text='/!\\Intruder in the zone/!\\', font=("Purisa",12,"bold","italic"), bg='red');
		# Label title
		main_l = Label(win, text='Drones interception simulation', font=("Purisa",12,"bold","italic"));
		main_l.grid(row=1, column=1, padx=10, pady=10);
		
		HEIGHT_CANVAS = HEIGHT*0.8;
		WIDTH_CANVAS = WIDTH*0.66;
		
		canvas_c = Canvas(win, width = WIDTH_CANVAS, height = HEIGHT_CANVAS, bg ='green');
		canvas_c.grid(row=3, column=1, rowspan=20, padx=10, pady=10);

		# Scope scale
		scale_l = Label(win, text='Scope value :');
		scale_l.grid(row=3, column=2);
		scale_s = Scale(win, from_=1, to=REAL_SCOPE*2, orient=HORIZONTAL, length=300, command=lambda CANVAS_C = canvas_c: self.draw_radar(scale_s.get(), WIDTH_CANVAS, HEIGHT_CANVAS, HEIGHT_SCALE, canvas_c));
		scale_s.set(REAL_SCOPE);

		scale_s.grid(row=4, column=2);

		# Add "ennemi"
		intruder_b = Button(win, text='Add intruder', command=lambda CANVAS_C = canvas_c: self.add_intruder(scale_s.get(), WIDTH_CANVAS, HEIGHT_CANVAS, HEIGHT_SCALE, CANVAS_C, warning_l, intruder_b));
		intruder_b.grid(row=5, column=2);

		# exit button
		quit_b = Button(win,text='Quit', command=quit);
		quit_b.grid(row=20, column=2, padx=10, pady=10);
		
		win.mainloop();
