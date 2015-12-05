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

time_sleep            = 0.001;
# Real scope in meter
REAL_SCOPE            = 350;
# Virtual scope in px
VIRTUAL_SCOPE         = 0;
# Height of the zone in meter
HEIGHT_ZONE           = 400;
# With of the zone in meter
WIDTH_ZONE            = 495;
# ration between px and meter
DIMENSION_COEFFICIENT = 2;
# In px
HEIGHT_CANVAS         = HEIGHT_ZONE * DIMENSION_COEFFICIENT;
# In px
WIDTH_CANVAS          = WIDTH_ZONE * DIMENSION_COEFFICIENT;
# Drone send while an attack
NUMBER_ALLY_DRONE     = 2;
# Initial stock of drone
NUMBER_DRONE          = 2;
# General shutdown
CONTINUE              = True;
# Origine = position of the radar
ORIGINE_Y             = HEIGHT_ZONE * DIMENSION_COEFFICIENT;

drone_out            = 0;
drone_ready          = 2;
drone_flying         = 3;
drone_back           = 4;	# Drone back of a mission ready for inspection
drone_ennemi_ready   = 7;
drone_ennemi_escaped = 8;

class Window():

	def get_repare_b(self):
		return self.repare_b;
		
	def get_origine_Y(self):
		return ORIGINE_Y;

	def get_width_zone(self):
		return WIDTH_ZONE;

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
		self.intruder_b = Button(self.win, text='Add target', width=50, height=50, command=lambda: self.add_ennemi());
		self.intruder_b.config(image=self.logo);
		self.intruder_b.grid(row=5, column=2, columnspan=2);

	def create_drone_label(self):

		global NUMBER_DRONE;
		num = 0;
		col = 2;
		line = 6;
		# Drones label
		for num in range(NUMBER_DRONE):
			name = "DRONE "+str(num+1);
			name = Label(self.win, text=name+"\nReady", relief=RAISED, width=10, height=5, bg="green");
			self.label_list.append(name);
			name.grid(row=line, column=col, padx=10, pady=10);
			col = col + 1;
			if col == 4:
				col = 2;
				line = line + 1;

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
		with_scale_line = 3
		self.CANVAS_C = Canvas(self.win, width = WIDTH_CANVAS, height = HEIGHT_CANVAS, bg ='#30A030', bd=5, relief=SUNKEN);
		self.CANVAS_C.grid(row=3, column=1, rowspan=20, padx=10, pady=10);
		self.CANVAS_C.create_line(20, ORIGINE_Y, 20 + 50, ORIGINE_Y, width=with_scale_line);
		self.CANVAS_C.create_line(20, ORIGINE_Y - 5, 20, ORIGINE_Y + 5, width=with_scale_line);
		self.CANVAS_C.create_line(20 + 50, ORIGINE_Y - 5, 20 + 50, ORIGINE_Y + 5, width=with_scale_line);
		self.CANVAS_C.create_text(20 + 25, ORIGINE_Y - 8, text="25m", font=("Purisa",13,"bold"));

	def create_title_label(self):
		# Label title
		self.main_l = Label(self.win, text='Drones interception simulation', font=("Purisa",12,"bold","italic"));
		self.main_l.grid(row=1, column=1, padx=10, pady=10);

	def create_repare_button(self):
		
		self.repare_b = Button(self.win, text='Repare drones', command=lambda:self.repare_drone());

	def repare_drone(self):	
		p = 30;
		temp_pop_list = [];
		temp_append_list = [];

		self.CANVAS_C.delete(self.win,"ennemi");
		self.CANVAS_C.delete(self.win,"drone");
		self.CANVAS_C.delete(self.win,"alt");
		self.CANVAS_C.delete(self.win,"text");
		self.CANVAS_C.delete(self.win,"line");
		for thread in self.thread_list:

			if thread.kind == "ally" and thread.state in (drone_back, drone_out, drone_flying):
				X = ((WIDTH_ZONE - NUMBER_DRONE * p) / 2 + p * thread.id + p/2) * DIMENSION_COEFFICIENT;
				Y = ORIGINE_Y - 20 * DIMENSION_COEFFICIENT;
				Z = 0;

				drone = Drone(self.CANVAS_C, thread.id, X, Y, Z, self.thread_list, self.label_list[thread.id], 0, -1);
				temp_append_list.append(drone);
				thread.label.config(bg="green", text="DRONE "+str(thread.id+1)+"\nReady");
				temp_pop_list.append(thread.id);
	
		for index in temp_pop_list:
			for thread in self.thread_list:
				if (thread.kind == "ally" and thread.id == index) or (thread.kind == "ennemi"):
					self.thread_list.pop(self.thread_list.index(thread));

		for drone in temp_append_list:
			self.thread_list.append(drone);
		self.repare_b.grid_forget();

	def create_quit_button(self):
		# exit button
		self.quit_b = Button(self.win,text='Exit', command=lambda:self.exit(self.win, False));
		self.quit_b.grid(row=20, column=2, columnspan=2);

	def settings(self):

		global NUMBER_DRONE;
		global REAL_SCOPE;
		retour = 0;

		self.nbDroneByAttack_l = Label(self.win, text='Drones for interception :');
		self.nbDroneByAttack_l.grid(row=16, column=2, columnspan=2);
		self.nbDroneByAttack_s = Scale(self.win, from_=1, to=NUMBER_DRONE, orient=HORIZONTAL, length=200, command=lambda code=retour:self.updateSettingsAlly());
		self.nbDroneByAttack_s.set(NUMBER_ALLY_DRONE)
		self.nbDroneByAttack_s.grid(row=17, column=2, columnspan=2);
		# Scope scale
		self.scale_l = Label(self.win, text='Scope value :');
		self.scale_l.grid(row=18, column=2, columnspan=2);
		self.scale_s = Scale(self.win, from_=1, to=REAL_SCOPE*2, orient=HORIZONTAL, length=200, command=lambda code=retour:self.draw_radar_zone());
		self.scale_s.set(REAL_SCOPE);
		self.scale_s.grid(row=19, column=2, columnspan=2);

		

	def updateSettingsAlly(self):

		global NUMBER_ALLY_DRONE;
		NUMBER_ALLY_DRONE = self.nbDroneByAttack_s.get();
		code = 0;
		return code;

	def draw_radar_zone(self):

		global VIRTUAL_SCOPE;
		global REAL_SCOPE;

		# Detection zone 

		self.CANVAS_C.delete("ennemi_0");
		self.CANVAS_C.delete("alt_0");
		self.CANVAS_C.delete("arcs");

		VIRTUAL_SCOPE = REAL_SCOPE * DIMENSION_COEFFICIENT;

		x0 = WIDTH_CANVAS / 2;
		y0 = ORIGINE_Y;
		r = 20;

		while r < VIRTUAL_SCOPE:
			circle = self.CANVAS_C.create_circle_arc(x0, y0, r, style='arc', outline="red", width=2, start=0, end=180, tags="arcs");
			self.CANVAS_C.tag_lower(circle);
			r += 10;

		try:
			REAL_SCOPE = self.scale_s.get();
		except:
			pass;

		code = 1;
		return code;

	def add_ennemi(self):
		
		global WIDTH_CANVAS;

		#self.intruder_b.config(state=DISABLED);
		#self.scale_s.config(state=DISABLED);
		
		X = random.uniform(0, WIDTH_CANVAS);
		Y = 0;
		# Dimension in Z is in meter
		Z = 200;

		ennemi = Ennemi(self.CANVAS_C, X, Y, Z, self.thread_list, []);
		
		self.thread_list.append(ennemi);
		ennemi.start();

	def exit(self, window, value):

		global CONTINUE;
		CONTINUE = value;
		time.sleep(0.2);
		#if window == self.win and self.settings:
		#	self.settings.destroy();
		window.destroy();

	def __init__(self, thread_list):

		self.thread_list = thread_list;

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
		
		self.draw_radar_zone();
		
		self.create_quit_button();

		self.settings();

		#---------------------------------------------------------------------------------------------------------------#
		#---------------------------------------------------------------------------------------------------------------#
		#---------------------------------------------------------------------------------------------------------------#

		



