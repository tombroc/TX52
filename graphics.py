#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*-iso-8859-15 -*
import os
from drone import Drone
from ennemi import Ennemi
from radar import Radar
from tkinter import *
import time
import random

REAL_SCOPE = 350;
REAL_SCOPE_SCALE = REAL_SCOPE;
VIRTUAL_SCOPE = 0;
# Height equivalency (in meters)
HEIGHT_SCALE = 400;
HEIGHT_CANVAS = 800;
WIDTH_CANVAS = 990;
NUMBER_ALLY_DRONE = 2;
NUMBER_DRONE = 6;
CONTINUE = True;
ORIGINE_Y = HEIGHT_CANVAS;

class Window():

	def get_repare_b(self):
		return self.repare_b;

	def get_noDrone_l(self):
		return self.noDrone_l;
		
	def get_origine_Y(self):
		return ORIGINE_Y;

	def get_width_canvas(self):
		return WIDTH_CANVAS;

	def get_ennemi_list(self):
		return self.ennemi_list;

	def get_canvas(self):
		return self.CANVAS_C;

	def get_intruder_b(self):
		return self.intruder_b;

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

	def create_ennemi_button(self):
		# Kind of a drone
		KIND_ENNEMI = "ennemi";
		# Add "ennemi" button
		self.logo = PhotoImage(file="images/cible.gif");
		self.intruder_b = Button(self.win, text='Add target', width=50, height=50, command=lambda: self.add_ennemi(KIND_ENNEMI, 0));
		self.intruder_b.config(image=self.logo);
		self.intruder_b.grid(row=5, column=2, columnspan=2);

	def create_drone_label(self):

		global NUMBER_DRONE;
		num = 0;
		# Drones label
		for num in range(NUMBER_DRONE):

			name = "DRONE "+str(num+1);
			name = Label(self.win, text=name+"\nReady", relief=RAISED, width=10, height=5, bg="green");
			self.label_list.append(name);
			if num < 2:
				name.grid(row=6, column=num+2, padx=10, pady=10);

			elif num < 4:
				name.grid(row=7, column=num+2-2, padx=10, pady=10);
			else:
				name.grid(row=8, column=num+2-4, padx=10, pady=10);

		self.noDrone_l = Label(self.win, text="No drone available", relief=RAISED);

	def create_main_window(self):

		global HEIGHT_CANVAS;
		global WIDTH_CANVAS;
		# Main window
		self.win = Tk();
		self.win.title("Drone interception");
		HEIGHT = 1000;
		WIDTH = 1300;
		
		
		self.win.geometry("%dx%d%+d%+d" % (WIDTH,HEIGHT_CANVAS + 100,(self.win.winfo_screenwidth()-WIDTH)/2,(self.win.winfo_screenheight()-HEIGHT)/2));

	def create_simulation_zone(self):
		# Simulation zone

		self.CANVAS_C = Canvas(self.win, width = WIDTH_CANVAS, height = HEIGHT_CANVAS, bg ='#30A030', bd=5, relief=SUNKEN);
		self.CANVAS_C.grid(row=3, column=1, rowspan=20, padx=10, pady=10);
		
	def create_title_label(self):
		# Label title
		self.main_l = Label(self.win, text='Drones interception simulation', font=("Purisa",12,"bold","italic"));
		self.main_l.grid(row=1, column=1, padx=10, pady=10);

	def create_repare_button(self):
		
		self.repare_b = Button(self.win, text='Repare drones')#, command=lambda:self.repare_drone());

	def repare_drone(self):	

		drone_ready = 2;
		drone_back  = 4;
		for i in range(NUMBER_DRONE):
			if self.drone_list[i].state == drone_back:
				self.drone_list[i].state = drone_ready;
		self.noDrone_l.grid_forget();
		self.repare_b.grid_forget();

	def create_settings_button(self):
		# Settings
		#self.settings_i = PhotoImage(file="settings.gif");
		self.logo_settings = PhotoImage(file="images/settings.GIF");
		self.settings_b = Button(self.win, text="Settings", command=lambda:self.settings_window());#image=self.settings_i);
		self.settings_b.config(image=self.logo_settings);
		self.settings_b.grid(row=20, column=2);

	def create_quit_button(self):
		# exit button
		self.quit_b = Button(self.win,text='Exit', command=lambda:self.exit(self.win, False));
		self.quit_b.grid(row=20, column=3, padx=10, pady=10);

	def settings_window(self):

		global NUMBER_DRONE;
		global REAL_SCOPE_SCALE;
		retour = 0;

		#Settings window
		self.settings = Tk();
		self.settings.title("Settings");
		self.settings.geometry("%dx%d%+d%+d" % (350,200,(self.win.winfo_screenwidth()-1400)/2,(self.win.winfo_screenheight()-1000)/2));
		self.nbDroneByAttack_s = Scale(self.settings, from_=1, to=NUMBER_DRONE, orient=HORIZONTAL);
		self.nbDroneByAttack_s.set(NUMBER_ALLY_DRONE)
		self.nbDroneByAttack_s.grid(row=1, column=1, columnspan=2);
		# Scope scale
		self.scale_l = Label(self.settings, text='Scope value :');
		self.scale_l.grid(row=2, column=1, columnspan=2);
		self.scale_s = Scale(self.settings, from_=1, to=REAL_SCOPE*2, orient=HORIZONTAL, length=300, command=lambda code=retour:self.draw_radar_zone());
		self.scale_s.set(REAL_SCOPE_SCALE);
		self.scale_s.grid(row=3, column=1, columnspan=2, padx=25);

		self.updateSettings_b = Button(self.settings, text="Validate", command=lambda:self.updateSettings(self.settings));
		self.updateSettings_b.grid(row=4, column=1, pady=25, columnspan=2);
		
		self.settings.mainloop();

	def updateSettings(self, window):

		global NUMBER_ALLY_DRONE;

		print("Updating settings...");
		NUMBER_ALLY_DRONE = self.nbDroneByAttack_s.get();
		self.draw_radar_zone();
		print ("Number ally drone = "+str(NUMBER_ALLY_DRONE));
		print ("Scope = "+str(NUMBER_ALLY_DRONE));
		self.exit(window, True);

	def draw_radar_zone(self):

		global VIRTUAL_SCOPE;
		global HEIGHT_SCALE;
		global HEIGHT_CANVAS;
		global REAL_SCOPE_SCALE;

		# Detection zone 

		self.CANVAS_C.delete("ennemi_0");
		self.CANVAS_C.delete("alt_0");
		self.CANVAS_C.delete("arcs");

		VIRTUAL_SCOPE = REAL_SCOPE_SCALE * HEIGHT_CANVAS / HEIGHT_SCALE;

		x0 = WIDTH_CANVAS / 2;
		y0 = ORIGINE_Y;
		r = 20;

		while r < VIRTUAL_SCOPE:
			circle = self.CANVAS_C.create_circle_arc(x0, y0, r, style='arc', outline="red", width=2, start=0, end=180, tags="arcs");
			self.CANVAS_C.tag_lower(circle);
			r += 10;

		try:
			REAL_SCOPE_SCALE = self.scale_s.get();
		except:
			pass;

		code = 1;
		return code;

	def add_ennemi(self, KIND, IDENTIFIER):
		
		global WIDTH_CANVAS;

		self.intruder_b.config(state=DISABLED);
		#self.scale_s.config(state=DISABLED);
		
		X = random.uniform(0, WIDTH_CANVAS);
		Y = 0;
		Z = 200;

		thread_drone = Ennemi(KIND, IDENTIFIER, self.CANVAS_C, X, Y, Z, self.ennemi_list, self.drone_list, []);
		
		self.ennemi_list.append(thread_drone);

		thread_drone.start();

	def exit(self, window, value):

		global CONTINUE;
		CONTINUE = value;
		time.sleep(0.2);
		#if window == self.win and self.settings:
		#	self.settings.destroy();
		window.destroy();

	def __init__(self, drone_list):

		self.ennemi_list = [];
		self.drone_list  = drone_list;
		self.label_list  = [];

		#---------------------------------------------------------------------------------------------------------------#
		#---------------------------------------------------------------------------------------------------------------#
		#---------------------------------------------------------------------------------------------------------------#

		self.create_main_window();

		self.create_simulation_zone();
		
		self.create_title_label();

		self.create_drone_label();

		self.create_repare_button();
		
		self.create_ennemi_button();

		self.create_settings_button();
		
		self.draw_radar_zone();
		
		self.create_quit_button();
		

		#---------------------------------------------------------------------------------------------------------------#
		#---------------------------------------------------------------------------------------------------------------#
		#---------------------------------------------------------------------------------------------------------------#

		



