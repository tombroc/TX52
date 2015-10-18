#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*-iso-8859-15 -*
import os
from drone import Drone
from radar import Radar
from tkinter import *
import time
import random

REAL_SCOPE = 350;
VIRTUAL_SCOPE = 0;
# Height equivalency (in meters)
HEIGHT_SCALE = 400;
HEIGHT_CANVAS = 0;
WIDTH_CANVAS = 0;
NUMBER_ALLY_DRONE = 1;
CONTINUE = True;

class Application():

	def get_height_canvas(self):
		return HEIGHT_CANVAS;

	def get_width_canvas(self):
		return WIDTH_CANVAS;

	def get_ennemi_list(self):
		return self.ennemi_list;

	def get_CANVAS_C(self):
		return self.CANVAS_C;

	def get_label_list(self):
		return self.label_list;

	def get_window(self):
		return self.win;

	def _create_circle_arc(self, x, y, r, **kwargs):
		if "start" in kwargs and "end" in kwargs:
			kwargs["extent"] = kwargs["end"] - kwargs["start"]
			del kwargs["end"]
			return self.create_arc(x-r, y-r, x+r, y+r, **kwargs)


	Canvas.create_circle_arc = _create_circle_arc;

	def draw_radar(self):

		global VIRTUAL_SCOPE;
		global HEIGHT_SCALE;
		global HEIGHT_CANVAS;


		# Detection zone 

		self.CANVAS_C.delete("ennemi_0");
		self.CANVAS_C.delete("alt_0");
		self.CANVAS_C.delete("arcs");

		VIRTUAL_SCOPE = self.scale_s.get() * HEIGHT_CANVAS / HEIGHT_SCALE;

		x0 = WIDTH_CANVAS / 2;
		y0 = HEIGHT_CANVAS;
		r = 20;

		while r < VIRTUAL_SCOPE:
			self.CANVAS_C.create_circle_arc(x0, y0, r, style='arc', outline="red", width=2, start=0, end=180, tags="arcs");
			r += 10;
		code = 1;
		return code;

	def add_ennemi(self, KIND, IDENTIFIER):
		
		global HEIGHT_CANVAS;
		global WIDTH_CANVAS;
		global HEIGHT_SCALE;
		print("100")

		self.intruder_b.config(state=DISABLED);
		self.scale_s.config(state=DISABLED);
		
		X = random.uniform(0, WIDTH_CANVAS);
		Y = 0;
		Z = 200;
		self.warning_l.grid_forget();

		thread_drone = Drone(KIND, IDENTIFIER, self.CANVAS_C, X, Y, Z, self.ennemi_list, []);
		
		self.ennemi_list.append(thread_drone);

		thread_drone.start();

		code = 1;
		return code;


	def get_canvas(self):
		return self.CANVAS_C;

	def get_app(self):
		return self;
	
	def exit(self):
		global CONTINUE;
		CONTINUE = False;
		quit();

	def __init__(self):


		global REAL_SCOPE;
		
		# Height equivalency (in meters)
		global HEIGHT_SCALE;

		# Scope at scale
		global VIRTUAL_SCOPE;

		global HEIGHT_CANVAS;
		global WIDTH_CANVAS;
		global CONTINUE;

		self.ennemi_list = [];

		self.label_list = [];
		# Kind of a drone
		KIND_ENNEMI = "ennemi";
		KIND_ALLY = "ally";

		retour = 0;

		num = 0;


		#---------------------------------------------------------------------------------------------------------------#
		#---------------------------------------------------------------------------------------------------------------#
		#---------------------------------------------------------------------------------------------------------------#


		# Main window
		self.win = Tk();
		self.win.title("Drone interception");
		
		# Simulation zone

		HEIGHT = 1000;
		WIDTH = 1400
		
		self.win.geometry("%dx%d%+d%+d" % (WIDTH,HEIGHT,(self.win.winfo_screenwidth()-WIDTH)/2,(self.win.winfo_screenheight()-HEIGHT)/2));
		
		HEIGHT_CANVAS = 800;
		WIDTH_CANVAS = 990;

		self.warning_l = Label(self.win, text='/!\\Intruder in the zone/!\\', font=("Purisa",12,"bold","italic"), bg='red');
		
		# Label title
		self.main_l = Label(self.win, text='Drones interception simulation', font=("Purisa",12,"bold","italic"));
		self.main_l.grid(row=1, column=1, padx=10, pady=10);

		self.CANVAS_C = Canvas(self.win, width = WIDTH_CANVAS, height = HEIGHT_CANVAS, bg ='#30A030', bd=5, relief=SUNKEN);
		self.CANVAS_C.grid(row=3, column=1, rowspan=20, padx=10, pady=10);
		

		# Scope scale
		self.scale_l = Label(self.win, text='Scope value :');
		self.scale_l.grid(row=3, column=2, columnspan=2);
		self.scale_s = Scale(self.win, from_=1, to=REAL_SCOPE*2, orient=HORIZONTAL, length=300, command=lambda code=retour: self.draw_radar());
		self.scale_s.set(REAL_SCOPE);
		self.scale_s.grid(row=4, column=2, columnspan=2);
		
		# Drones label
		while num < 6:
			num += 1;
			name = "DRONE "+str(num)
			name = Label(self.win, text=name, relief=RAISED, width=10, height=5, bg="green");
			self.label_list.append(name);
			if num < 3:
				name.grid(row=6, column=num+1);
			elif num < 5:
				name.grid(row=7, column=num+1-2);
			else:
				name.grid(row=8, column=num+1-4);

		# Add "ennemi" button
		self.intruder_b = Button(self.win, text='Add intruder', command=lambda code=retour: self.add_ennemi(KIND_ENNEMI, 0));
		self.intruder_b.grid(row=5, column=2, columnspan=2);

		# exit button
		self.quit_b = Button(self.win,text='Exit', command=lambda:self.exit());

		self.quit_b.grid(row=20, column=2, padx=10, pady=10);
		

		#---------------------------------------------------------------------------------------------------------------#
		#---------------------------------------------------------------------------------------------------------------#
		#---------------------------------------------------------------------------------------------------------------#

