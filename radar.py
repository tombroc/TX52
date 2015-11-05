#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*-iso-8859-15 -*
import os
import graphics as g
from drone import Drone
from tkinter import *
from threading import Thread, RLock
from math import sqrt
import time
import random


class Radar(Thread):
	def __init__(self, drone_list, ennemi_list, CANVAS_C, label_list, intruder_b, noDrone_l):
		Thread.__init__(self);
		self.drone_list  = drone_list;
		self.ennemi_list = ennemi_list;
		self.canvas      = CANVAS_C;
		self.label_list  = label_list;
		self.intruder_b  = intruder_b;
		self.noDrone_l   = noDrone_l;

	def run(self):

		# Possible state of a drone
		drone_out             = 0;	# Drone down (ennemi as well as ally)
		drone_backprogress    = 1;	# Drone is coming back of his mission
		drone_ready           = 2;	# Drone on his spot and operational
		drone_flying          = 3;	# Drone in mission flying through the target
		drone_back            = 4;	# Drone back of a mission ready for inspection
		drone_destroyed       = 5;	# Drone destroyed during a mission
		drone_ennemi_detected = 6;	# Drone ennemi detected
		drone_ennemi_ready    = 7;	# Drone ennemi ready
		drone_ennemi_escaped  = 8;
			
		print ("---- STARTING DETECTION ----");
		intruder = 0;
		while g.CONTINUE:
			if not self.drone_list:
				self.label_list["noDrone"].grid(row=2, column=8, columnspan=4);
			for ennemi in self.ennemi_list:
				if sqrt(
							  (ennemi.X - (g.WIDTH_CANVAS)/2) * (ennemi.X - (g.WIDTH_CANVAS)/2) 
				  		  	+ (ennemi.Y - (g.HEIGHT_CANVAS)) * (ennemi.Y - (g.HEIGHT_CANVAS))
						  ) <= g.VIRTUAL_SCOPE and ennemi.state == drone_ennemi_ready:
					intruder = 1;
					ennemi.state = drone_ennemi_detected;

					print("---- INTRUDER IN THE ZONE : "+str(intruder)+" ----")
				elif ennemi.state == drone_out:
					self.ennemi_list.pop(ennemi.id);
			mission = 0;
			for i in range(6):
				if self.drone_list[i].state in (drone_flying, drone_backprogress):
					mission = 1;
			if not self.ennemi_list and mission == 0:
				self.intruder_b.config(state=NORMAL);
			if intruder == 1:
				i = 0;
				num = 0;
				print (g.NUMBER_ALLY_DRONE)
				while num < g.NUMBER_ALLY_DRONE and i < 6:
					if self.drone_list[i].state == drone_ready:
						print ("Drone "+str(i)+" ready");
						self.drone_list[i].state = drone_flying;
						self.drone_list[i].start();
						self.label_list[i].config(bg="yellow", text="DRONE "+str(i+1)+"\nIn misson");

						num += 1
					i += 1;
					if num == 0 and i == 5:
						self.noDrone_l.grid(row=9, column=2, columnspan=4);

			intruder = 0;
		
			time.sleep(0.1);





