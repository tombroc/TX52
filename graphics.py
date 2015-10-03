#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*-iso-8859-15 -*
import os
from drone import Drone
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

		CANVAS_C.delete("ennemi_0");
		CANVAS_C.delete("alt_0");
		CANVAS_C.delete("arcs");
		VIRTUAL_SCOPE = REAL_SCOPE * HEIGHT_CANVAS / HEIGHT_SCALE;
	
		x0 = WIDTH_CANVAS / 2;
		y0 = HEIGHT_CANVAS;
		r = 20;

		while r < VIRTUAL_SCOPE:
			CANVAS_C.create_circle_arc(x0, y0, r, style='arc', outline="red", width=2, start=0, end=180, tags="arcs");
			r += 10;

		return CANVAS_C;
	
	def add_drone(self, REAL_SCOPE, WIDTH_CANVAS, HEIGHT_CANVAS, HEIGHT_SCALE, CANVAS_C, warning_l, intruder_b, scale_s, KIND, IDENTIFIER):
		
		# To improve by using threads
		intruder_b.config(state=DISABLED);
		scale_s.config(state=DISABLED);
		Z = 20;
		Y = 1;
		X = random.uniform(0, WIDTH_CANVAS);
		dX = 0;
		dY = 1;


		warning_l.grid_forget();
		CANVAS_C.delete("ennemi_0");
		CANVAS_C.delete("alt_0");
		
		intruder = Drone(KIND, IDENTIFIER, CANVAS_C, X, Y, Z);
		
		VIRTUAL_SCOPE = REAL_SCOPE * HEIGHT_CANVAS / HEIGHT_SCALE;
		
		# For the simulation : the ennemi can approach until we decide it's enough

		while (
				sqrt(
						(X - (WIDTH_CANVAS/2)) * (X - (WIDTH_CANVAS/2)) 
					  + (Y - (HEIGHT_CANVAS)) * (Y - (HEIGHT_CANVAS))
					) > VIRTUAL_SCOPE):

			if X <= WIDTH_CANVAS/2:
				a = -1;
				b = 2;
				dX = random.uniform(a, b);
			elif X >= WIDTH_CANVAS/2:
				a = -2;
				b = 1;
				dX = random.uniform(a, b);

			if Z < 3:
				dZ = 2;
			else:
				dZ = random.randint(-1,1);

			X, Y, Z = intruder.move(X, Y, Z, dX, dY, dZ, CANVAS_C, intruder);

			time.sleep(0.05);
		warning_l.grid(row=9, column=2,columnspan=2);
		scale_s.config(state=NORMAL);	
		intruder_b.config(state=NORMAL);

	def __init__(self):

		
		# GLOBAL VARIABLES
		#def main(self):
		# CAPTOR SCALE
		REAL_SCOPE = 200;
		
		# Height equivalency (in meters)
		HEIGHT_SCALE = 400;

		# Scope at scale
		VIRTUAL_SCOPE = 0;

		# Kind of a drone
		KIND_ENNEMI = "ennemi";
		KIND_ALLY = "ally";

		# For tests : only one ennemi 
		ENNEMI_ID = "0";

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
		
		canvas_c = Canvas(win, width = WIDTH_CANVAS, height = HEIGHT_CANVAS, bg ='#30A030', bd=5, relief=SUNKEN);
		canvas_c.grid(row=3, column=1, rowspan=20, padx=10, pady=10);

		# Scope scale
		scale_l = Label(win, text='Scope value :');
		scale_l.grid(row=3, column=2, columnspan=2);
		scale_s = Scale(win, from_=1, to=REAL_SCOPE*2, orient=HORIZONTAL, length=300, command=lambda CANVAS_C = canvas_c: self.draw_radar(scale_s.get(), WIDTH_CANVAS, HEIGHT_CANVAS, HEIGHT_SCALE, canvas_c));
		scale_s.set(REAL_SCOPE);
		scale_s.grid(row=4, column=2, columnspan=2);

		# Drones label
		num = 0;
		while num < 6:
			num += 1;
			name = "DRONE "+str(num)
			name = Label(win, text=name, relief=RAISED, width=10, height=5, bg="green");
			if num < 3:
				name.grid(row=6, column=num+1);
			elif num < 5:
				name.grid(row=7, column=num+1-2);
			else:
				name.grid(row=8, column=num+1-4);
		# Add "ennemi"
		intruder_b = Button(win, text='Add intruder', command=lambda CANVAS_C = canvas_c: self.add_drone(scale_s.get(), WIDTH_CANVAS, HEIGHT_CANVAS, HEIGHT_SCALE, CANVAS_C, warning_l, intruder_b, scale_s, KIND_ENNEMI, ENNEMI_ID));
		intruder_b.grid(row=5, column=2, columnspan=2);

		# exit button
		quit_b = Button(win,text='Quit', command=quit);
		quit_b.grid(row=20, column=2, padx=10, pady=10);
		
		win.mainloop();
