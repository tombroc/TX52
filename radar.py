#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*-iso-8859-15 -*
import os
import graphics as g
from drone import Drone
from tkinter import *
from threading import Thread, RLock, Event
from math import sqrt
import time
import random


class Radar(Thread):
	def __init__(self, thread_list, CANVAS_C, label_list, intruder_b, repare_b):
		Thread.__init__(self);
		self.id           = len(thread_list);
		self.thread_list  = thread_list;
		self.event        = Event();
		self.canvas       = CANVAS_C;
		self.label_list   = label_list;
		self.intruder_b   = intruder_b;
		self.repare_b     = repare_b;
		self.state_thread = "ON";
		self.kind         = "radar";

		self.event.set();

	def thread_traitment(self):
		
		# If there is only on thread, it keeps running...
		next_thread_id = 0;

		if len(self.thread_list) > 1:
			# If the test return the last element of the list
			#print ("len(self.thread_list)-1 : "+str(len(self.thread_list)-1));
			if self.id == len(self.thread_list)-1:
				#print ("Last thread of the list -> go back to the first one");
				#print ("Previous thread id : "+str(self.id));
				next_thread_id = 0;
			else: 
				#print ("Not the last thread of the list -> go to the next one");
				#print ("Previous thread id : "+str(self.id));
				next_thread_id = self.id+1;
			#print ("Next thread id : "+str(next_thread_id));
			#print ("len(self.thread_list) "+str(len(self.thread_list)));
			#print ("next_thread_id "+str(next_thread_id))
			while self.thread_list[next_thread_id].state_thread != "ON" and g.CONTINUE:
				if next_thread_id == len(self.thread_list)-1:
					next_thread_id = 0;
				else:
					next_thread_id = next_thread_id + 1;

			if self.id == len(self.thread_list)-1:
				next_thread_id = 0;
			#print ("Changing thread from "+str(self.kind) +" "+str(self.id+1)+" to "+str(self.kind) +" "+str(self.thread_list[next_thread_id].id+1));
			self.thread_list[next_thread_id].event.clear();
			self.thread_list[next_thread_id].event.set();
			time.sleep(g.time_sleep);
			self.event.wait();

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
			self.thread_traitment();
			num_ennemi = 0;
			for thread in self.thread_list:
				#print ("Not empty thread_list : "+str(thread.id));
				if thread.kind == "ennemi" and thread.state == drone_ennemi_ready and sqrt(
						  (thread.X - (g.WIDTH_CANVAS)/2) * (thread.X - (g.WIDTH_CANVAS)/2) 
			  		  	+ (thread.Y - (g.HEIGHT_CANVAS)) * (thread.Y - (g.HEIGHT_CANVAS))
					  ) <= g.VIRTUAL_SCOPE:
					num_ennemi = num_ennemi + 1;
					intruder = 1;
					ennemi_id = self.thread_list.index(thread);
					thread.state = drone_ennemi_detected;

					print("---- INTRUDER IN THE ZONE : "+ str(thread.kind)+" - "+str(num_ennemi)+" ----\n")
				elif thread.kind == "ennemi" and thread.state == drone_out:
					self.thread_list[thread.id].state_thread = "OFF";
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
					if thread.kind == "ally" and thread.state == drone_ready and num < g.NUMBER_ALLY_DRONE:
						print ("start drone"+str(thread.id))
						thread.state = drone_flying;
						thread.traject = self.canvas.create_line(thread.X, thread.Y, self.thread_list[ennemi_id].X, self.thread_list[ennemi_id].Y, tags="line");
						print ("ennemi_id = "+str(ennemi_id))
						thread.target_id = ennemi_id;
						thread.state_thread = "ON";
						thread.start();
						self.label_list[thread.id].config(bg="yellow", text="DRONE "+str(thread.id+1)+"\nIn mission");
						num += 1
					i += 1;	
				num = 0;
			for thread in self.thread_list:
				if thread.kind == "ally":
					if thread.state != drone_ready:
						num_not_ready = num_not_ready + 1;

			if num_not_ready == g.NUMBER_DRONE:
				self.repare_b.grid(row=16, column=2, columnspan=2);

				test = 0;
			intruder = 0;
		
			time.sleep(0.1);
		print ("---- ENDING DETECTION ----\n")




