#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*-iso-8859-15 -*
import os
import graphics as g
from drone import Drone
from tkinter import *
from threading import Thread, Event
from math import sqrt
import time
import random


class Radar(Thread):
	def __init__(self, utils, thread_list, CANVAS_C, label_list, repare_b):
		Thread.__init__(self);
		self.id           = len(thread_list);
		self.thread_list  = thread_list;
		self.event        = Event();
		self.canvas       = CANVAS_C;
		self.label_list   = label_list;
		self.repare_b     = repare_b;
		self.state_thread = "ON";
		self.kind         = "radar";
		self.state        = -1;
		self.utils = utils;

		self.event.set();

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
			
		print ("---- STARTING DETECTION ----\n");
		intruder = 0;
		while g.CONTINUE:
			self.utils.thread_traitment(True, self.thread_list.index(self));
			num_ennemi = 0;
			for thread in self.thread_list:
				if g.CONTINUE:
					if thread.kind == "ennemi" and thread.state == drone_ennemi_ready and sqrt(
							  (thread.X - (g.WIDTH_CANVAS)/2) * (thread.X - (g.WIDTH_CANVAS)/2) 
				  		  	+ (thread.Y - (g.HEIGHT_CANVAS)) * (thread.Y - (g.HEIGHT_CANVAS))
						  ) <= g.VIRTUAL_SCOPE:
						num_ennemi = num_ennemi + 1;
						intruder = 1;
						ennemi_id = thread.id;
						thread.state = drone_ennemi_detected;

						print("---- INTRUDER IN THE ZONE : "+ str(thread.kind)+" - "+str(num_ennemi)+" ----\n")
					elif thread.kind == "ennemi" and thread.state == drone_out:
						self.thread_list[self.thread_list.index(thread)].state_thread = "OFF";
					elif thread.kind == "ennemi":
						num_ennemi = num_ennemi + 1;

			mission = 0;

			for thread in self.thread_list:
				if thread.kind == "ally" and thread.state in (drone_flying, drone_backprogress):
					mission = 1;

			num = 0;
			num_not_ready = 0;
			if intruder == 1:
				i = 0;
				test = 0;

				for thread in self.thread_list:
					if thread.kind == "ally" and thread.state == drone_ready and num < g.NUMBER_ALLY_DRONE and g.CONTINUE:
						thread.state = drone_flying;
						for ennemi in self.thread_list:
							if ennemi.kind == "ennemi" and ennemi.id == ennemi_id:
								#thread.traject = self.canvas.create_line(thread.X, thread.Y, ennemi.X, ennemi.Y, tags="line");
								thread.target = ennemi;
						thread.state_thread = "ON";
						#thread.daemon = True;
						thread.start();
						#thread.join();
						self.label_list[thread.id].config(bg="yellow", text="DRONE "+str(thread.id+1)+"\nIn mission");
						num += 1
					i += 1;	
				num = 0;
			for thread in self.thread_list:
				if thread.kind == "ally" and g.CONTINUE:
					if thread.state not in (drone_ready, drone_flying):
						num_not_ready = num_not_ready + 1;

			if num_not_ready == g.NUMBER_DRONE:
				self.repare_b.grid(row=15, column=2, columnspan=2);

				test = 0;
			intruder = 0;
		self.state_thread = "OFF";
		print ("---- ENDING DETECTION ----\n")




