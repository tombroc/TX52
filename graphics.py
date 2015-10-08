#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*-iso-8859-15 -*
import os
from drone import Drone
from tkinter import *
import time
import random

REAL_SCOPE = 200;
VIRTUAL_SCOPE = 0;
# Height equivalency (in meters)
HEIGHT_SCALE = 400;
HEIGHT_CANVAS = 0;
WIDTH_CANVAS = 0;

class Application():
	def _create_circle_arc(self, x, y, r, **kwargs):
		if "start" in kwargs and "end" in kwargs:
			kwargs["extent"] = kwargs["end"] - kwargs["start"]
			del kwargs["end"]
			return self.create_arc(x-r, y-r, x+r, y+r, **kwargs)


	Canvas.create_circle_arc = _create_circle_arc;

	def draw_radar(self, HEIGHT_SCALE, scale_s):

		# Detection zone 

		self.CANVAS_C.delete("ennemi_0");
		self.CANVAS_C.delete("alt_0");
		self.CANVAS_C.delete("arcs");
		
		global VIRTUAL_SCOPE;
		VIRTUAL_SCOPE = scale_s.get() * HEIGHT_CANVAS / HEIGHT_SCALE;
		x0 = WIDTH_CANVAS / 2;
		y0 = HEIGHT_CANVAS;
		r = 20;

		while r < VIRTUAL_SCOPE:
			self.CANVAS_C.create_circle_arc(x0, y0, r, style='arc', outline="red", width=2, start=0, end=180, tags="arcs");
			r += 10;
		code = 1;
		return code;

	def add_drone(self, HEIGHT_SCALE, warning_l, intruder_b, scale_s, KIND, IDENTIFIER, drone_list):
		
		# To improve by using threads
		intruder_b.config(state=DISABLED);
		scale_s.config(state=DISABLED);
		if KIND == "ennemi":
			Z = 20;
			Y = 1;
			X = random.uniform(0, WIDTH_CANVAS);
			dX = 0;
			dY = 1;
			warning_l.grid_forget();
		
		VIRTUAL_SCOPE = REAL_SCOPE * HEIGHT_CANVAS / HEIGHT_SCALE;
		thread_drone = Drone(KIND, IDENTIFIER, self.CANVAS_C, X, Y, Z, self.win);
		drone_list.append(thread_drone);
		# For the simulation : the ennemi can approach until we decide it's enough
		thread_drone.start();		
		X, Y, Z = thread_drone.get_coords();
		print ("thread_drone coords : X = "+ str(X)+", Y = "+str(Y)+", Z = "+str(Z))
		warning_l.grid(row=9, column=2,columnspan=2);
		scale_s.config(state=NORMAL);	
		intruder_b.config(state=NORMAL);
		#	thread_drone.join();		

		return drone_list;

	def updtate_canvas(self, CANVAS_C, drone_list):
		print("---- INTO THE FUNCTION -----")	
		for drone in drone_list:		
			print ("---- MOVE ----")
			X0, Y0, X1, Y1, X2, Y2 = CANVAS_C.coords(drone.drone);
			CANVAS_C.move(drone.drone, drone.X - X0, drone.Y - Y0);
			CANVAS_C.coords(drone.alt_t, drone.X + drone.diameter, drone.Y + 2);
			CANVAS_C.itemconfig(drone.alt_t, text="Alt : "+str(drone.Z)+"m");
		CANVAS_C.update();

	def get_canvas(self):
		return self.CANVAS_C;

	def get_app(self):
		return self;

	def __init__(self):

		
		# GLOBAL VARIABLES
		#def main(self):
		# CAPTOR SCALE
		global REAL_SCOPE;
		
		# Height equivalency (in meters)
		global HEIGHT_SCALE;

		# Scope at scale
		global VIRTUAL_SCOPE;

		global HEIGHT_CANVAS;
		global WIDTH_CANVAS;
		# Kind of a drone
		KIND_ENNEMI = "ennemi";
		KIND_ALLY = "ally";

		# For tests : only one ennemi 
		ENNEMI_ID = "0";

		drone_list = [];
		# Main window
		self.win = Tk();
		self.win.title("Drones interseption");
		self.win.attributes('-fullscreen', 1);
		
		# Simulation zone
		HEIGHT = self.win.winfo_height();
		WIDTH = self.win.winfo_width();
		
		warning_l = Label(self.win, text='/!\\Intruder in the zone/!\\', font=("Purisa",12,"bold","italic"), bg='red');
		# Label title
		main_l = Label(self.win, text='Drones interception simulation', font=("Purisa",12,"bold","italic"));
		main_l.grid(row=1, column=1, padx=10, pady=10);
		
		
		HEIGHT_CANVAS = HEIGHT*0.8;
		WIDTH_CANVAS = WIDTH*0.66;

		self.CANVAS_C = Canvas(self.win, width = WIDTH_CANVAS, height = HEIGHT_CANVAS, bg ='#30A030', bd=5, relief=SUNKEN);
		self.CANVAS_C.grid(row=3, column=1, rowspan=20, padx=10, pady=10);

		retour = 0;
		# Scope scale
		scale_l = Label(self.win, text='Scope value :');
		scale_l.grid(row=3, column=2, columnspan=2);
		scale_s = Scale(self.win, from_=1, to=REAL_SCOPE*2, orient=HORIZONTAL, length=300, command=lambda code=retour: self.draw_radar(HEIGHT_SCALE, scale_s));
		scale_s.set(REAL_SCOPE);
		scale_s.grid(row=4, column=2, columnspan=2);

		# Drones label
		num = 0;
		while num < 6:
			num += 1;
			name = "DRONE "+str(num)
			name = Label(self.win, text=name, relief=RAISED, width=10, height=5, bg="green");
			if num < 3:
				name.grid(row=6, column=num+1);
			elif num < 5:
				name.grid(row=7, column=num+1-2);
			else:
				name.grid(row=8, column=num+1-4);
		# Add "ennemi"
		intruder_b = Button(self.win, text='Add intruder', command=lambda drone_list=drone_list: self.add_drone(HEIGHT_SCALE, warning_l, intruder_b, scale_s, KIND_ENNEMI, ENNEMI_ID, drone_list));
		intruder_b.grid(row=5, column=2, columnspan=2);

		# exit button
		quit_b = Button(self.win,text='Quit', command=quit);
		quit_b.grid(row=20, column=2, padx=10, pady=10);
		
		self.updtate_canvas(self.CANVAS_C, drone_list);
		
		self.win.mainloop();
