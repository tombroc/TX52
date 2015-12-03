#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*-iso-8859-15 -*
import os
import sys
import graphics as g
from tkinter import *
from threading import Thread, RLock, Event
from math import sqrt
import time
import random

loop_number          = 1;

drone_out            = 0;
drone_ready          = 2;
drone_flying         = 3;
drone_back           = 4;	# Drone back of a mission ready for inspection
drone_ennemi_ready   = 7;
drone_ennemi_escaped = 8;

class Drone(Thread):

	def __init__(self, CANVAS_C, X, Y, Z, thread_list, label, traject, target_id):
		Thread.__init__(self);
		drone_ready        = 2;	# Drone on his spot and operational
		drone_ennemi_ready = 7;	# Drone ennemi ready
		
		self.canvas        = CANVAS_C;
		self.id            = len(thread_list);
		self.kind          = "ally";
		self.diameter      = 20;
		self.height        = 5;
		self.X             = X;
		self.Y             = Y;
		self.Z             = Z;
		self.label         = label;
		self.event         = Event();
		self.traject       = traject;
		
		self.event.set();	
		tags               = "drone_";
		color              = "blue";
		position           = "ne"
		state              = drone_ready;
		offset             = -self.diameter;
		self.speed         = 0;
		self.speed_max     = 3;
		self.name_t        = CANVAS_C.create_text(self.X, self.Y+self.diameter+20, anchor="s", text="Drone "+str(self.id+1), tags="drone_"+ str(self.kind)+"_"+str(self.id+1), fill=color);
		self.X_SPOT        = X;
		self.Y_SPOT        = Y;
		self.Z_SPOT        = Z;
		
		alt                = "Alt : "+ str(self.Z) +"m";
		self.drone         = CANVAS_C.create_polygon(self.X, self.Y, self.X+self.diameter, self.Y+self.diameter, self.X-self.diameter, self.Y+self.diameter, tags=tags+str(self.id), fill=color);
		self.alt_t         = CANVAS_C.create_text(self.X+offset, self.Y+2, anchor=position, text=alt, tags="alt_"+ str(self.kind)+"_"+str(self.id+1), fill=color);
		self.state         = state;
		self.state_thread  = "OFF";
		self.target_id     = target_id;
		self.thread_list   = thread_list;

		self.event.set();

	# Tell the drone to go straight
	def go_straight(self, dY):
		return self.Y - dY;

	def go_back(self, dY):
		return self.Y + dY;

	def go_right(self, dX):
		return self.X + dX;

	def go_left(self, dX):
		return self.X - dX;

	def go_up(self, dZ):
		return self.Z + dZ;

	def go_down(self, dZ):
		return self.Z - dZ;

	def get_coords(self):
		return self.X, self.Y, self.Z;
	
	def abs(self, a):
		if a > 0:
			return a;
		else:
			return -a;

	def out_diameter(self, X, a):
		if a-self.diameter/2 <= X <= a+self.diameter/2:
			return False;
		else:
			return True;

	def in_diameter(self, X, a):
		if a-self.diameter/2 <= X <= a+self.diameter/2:
			return True;
		else:
			return False;

	def out_height(self, X, a):
		if a-self.height/2 <= X <= a+self.height/2:
			return False;
		else:
			return True;

	def in_height(self, X, a):
		if a-self.height/2 <= X <= a+self.height/2:
			return True;
		else:
			return False;

	def between(self, X, Y, a):
		if X > Y-a and X < Y+a:
			return True;
		else:
			return False;

	def compute_trajectory(self, a, b, TARGET_KIND):

		# Unitary vector
		
		newa = a / sqrt(a**2 + b**2);
		newb = b / sqrt(a**2 + b**2);
		
		# Parameter t

		t = self.speed;
		self.canvas.coords(self.traject, self.X, self.Y, self.X + (t*a), self.Y+ (t*b))
		
		# New coordinnates for the drone (using parametric system)

		newX = self.go_right(t * newa);
		newY = self.go_back(t * newb);
		newZ = self.Z;

		# Target is an ennemi
		if TARGET_KIND == 0:
			if self.thread_list[self.target_id].state_thread == "ON" and self.thread_list[self.target_id].Z > self.Z:
				newZ = self.go_up(1);
			elif self.thread_list[self.target_id].state_thread == "ON" and self.thread_list[self.target_id].Z < self.Z:
				newZ = self.go_down(1);

		# Target is QG
		# Stop 10meters above the QG spot
		elif self.Z > self.Z_SPOT + 10:
			newZ = self.go_down(0.1 * self.Z);
			

		if self.check_trajectory(newX, newY, newZ):

			self.canvas.move(self.drone, t * newa, t * newb);
			self.canvas.move(self.alt_t, t * newa, t * newb);
			self.canvas.move(self.name_t, t * newa, t * newb);

		self.canvas.itemconfig(self.alt_t, text="Alt : "+str(int(newZ))+"m");
		self.canvas.update();

		# Update of the drone coordinates

		self.X = newX;
		self.Y = newY;
		self.Z = newZ;

	def check_trajectory(self, X, Y, Z):
		dX = 1;
		for thread in self.thread_list:
			if thread.kind == "ally" and thread.id != self.id and thread.state == drone_flying:
				dist = sqrt( (X - thread.X)**2 + (Y - thread.Y)**2);
				#print ("dist = " +str(dist)+ " diameter = "+str(self.diameter))
				if  dist <= self.diameter + 2 and X < thread.X:
					print ("---- Trajectory correction : "+str(self.kind)+" - "+str(self.id) +" ----\n");
					# The drone must change his trajectory
					self.canvas.move(self.drone,  (X-self.X)*2, (Y-self.Y)/2);
					self.canvas.move(self.alt_t,  (X-self.X)*2, (Y-self.Y)/2);
					self.canvas.move(self.name_t, (X-self.X)*2, (Y-self.Y)/2);
					self.canvas.update();
					self.Y = self.go_straight((Y-self.Y)/2);
					if X < thread.X:
						self.X = self.go_left((X-self.X)*2);
					else: 
						self.X = self.go_right((X-self.X)*2);
					self.slowing_down_phase(1);
					return False;
				else:
					return True;
			else:
				# No other drone flying
				return True; 

	def slowing_down_phase(self, speed):
		COEFF_SLOW_DOWN = 0.05 * self.speed_max;
		if self.speed - COEFF_SLOW_DOWN >= speed:
			self.speed = self.speed - COEFF_SLOW_DOWN;

	def acceleration_phase(self):
		COEFF_ACCELERATION = 0.05 * self.speed_max;
		if self.speed + COEFF_ACCELERATION <= self.speed_max:
			self.speed = self.speed + COEFF_ACCELERATION;

	def takeoff_phase(self):
		if self.thread_list[self.target_id].Z > 8:
			while self.thread_list[self.target_id].state_thread == "ON" and self.thread_list[self.target_id] and self.Z < 10 and g.CONTINUE:
				self.thread_traitment();
				if self.Z > self.thread_list[self.target_id].Z:
					self.Z = self.Z - 1;
				elif self.Z < self.thread_list[self.target_id].Z:
					self.Z = self.Z + 1;
				self.canvas.itemconfig(self.alt_t, text="Alt : "+str(int(self.Z))+"m");
				self.canvas.update();
		else:
			while self.thread_list[self.target_id].state_thread == "ON" and not self.between(self.Z, self.thread_list[self.target_id].Z, 2) and g.CONTINUE:
				self.thread_traitment();
				if self.Z > self.thread_list[self.target_id].Z:
					self.Z = self.Z - 1;
				elif self.Z < self.thread_list[self.target_id].Z:
					self.Z = self.Z + 1;
				self.canvas.itemconfig(self.alt_t, text="Alt : "+str(int(self.Z))+"m");
				self.canvas.update();

	def landing_phase(self):
		# Go down until the drone touch the ground
			while self.Z > self.Z_SPOT and g.CONTINUE:
				self.thread_traitment();
				self.Z -= 0.1;
				self.canvas.itemconfig(self.alt_t, text="Alt : "+str(int(self.Z))+"m");
				self.canvas.update();
				time.sleep(g.time_sleep);

	def Uturn_phase(self, phase):
		print ("slowing down drone "+str(self.kind)+" "+str(self.id))
		if phase == 1:
			while int(self.speed) > 0:
				self.slowing_down_phase(0);
			self.speed = 0;
		elif phase == 2:
			while round(self.speed, 1) < self.speed_max:
				self.acceleration_phase();

	def comingback_phase(self):
		print ("Start coming back phase");
		#------ Back to GQ if the ennemi escaped or if another drone intersepted it ------#
		TARGET_KIND = 1;
		if ((self.thread_list[self.target_id].state_thread == "OFF"  or (self.thread_list[self.target_id].state == drone_ennemi_escaped)) and self.state == drone_flying) and g.CONTINUE:
			self.Uturn_phase(1);
			#print ("In if")
			i = 0;
			self.label.config(text="DRONE "+str(self.id+1)+"\nComing back");
			count = 0;
			slow_counter = 0;
			self.Uturn_phase(2);
			while (round(self.X, 0) != round(self.X_SPOT, 0) 
				or round(self.Y, 0) != round(self.Y_SPOT, 0)) and g.CONTINUE:
				print ("In the coming back loop")
				# i += 1;
				# if i == loop_number and self.ennemi_list:
				# 	i = 0;
				self.thread_traitment();

				if (self.abs(self.X-self.X_SPOT) < 100 or self.abs(self.Y-self.Y_SPOT) < 100):

					self.slowing_down_phase(1);
					if slow_counter == 0:
						print("Slowing down... drone "+str(self.kind)+" "+str(self.id));
						slow_counter = 1;
				else:
					slow_counter = 0;

				a = self.X_SPOT - self.X;
				b = self.Y_SPOT - self.Y;

				#print ("a = "+str(a)+" b = "+str(b)+" c = "+str(c));
				self.compute_trajectory(a, b, TARGET_KIND);

			print("Drone "+str(self.id)+" - Landing phase")
			self.landing_phase();
				
			if g.CONTINUE:
				self.state = drone_back;	# Drone back of a mission ready for inspection
				self.label.config(bg="blue", text="DRONE "+str(self.id+1)+"\nBack");
				# if the ennemi escaped we get him out of the list
				if self.thread_list[self.target_id].state_thread == "ON":
					self.thread_list[self.target_id].state = drone_out;

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

	def drone_movement(self):
		
		self.event.wait();
		#i = 0;
		TARGET_KIND = 0;
		# Takeoff phase
		self.takeoff_phase();
		#time.sleep(5);
		while (self.thread_list[self.target_id].state_thread == "ON" and (self.out_diameter(int(self.X), int(self.thread_list[self.target_id].X)) 
			or self.out_diameter(int(self.Y), int(self.thread_list[self.target_id].Y)) 
			or self.out_height(self.Z, self.thread_list[self.target_id].Z))
			and sqrt((self.thread_list[self.target_id].X - (g.WIDTH_CANVAS)/2) * (self.thread_list[self.target_id].X - (g.WIDTH_CANVAS)/2) + (self.thread_list[self.target_id].Y - (g.HEIGHT_CANVAS)) * (self.thread_list[self.target_id].Y - (g.HEIGHT_CANVAS))) <= g.VIRTUAL_SCOPE+15) and g.CONTINUE:
			

			#print ("Thread id : "+ str(self.id)+ " Kind : "+str(self.kind));
			self.thread_traitment();
			self.acceleration_phase();
			# Best trajectory to intercept the intruder

			# Direction vector between drone and ennemi
			if self.thread_list[self.target_id].state_thread == "ON":
				self.canvas.coords(self.traject, self.X, self.Y, self.thread_list[self.target_id].X, self.thread_list[self.target_id].Y);
				a = self.thread_list[self.target_id].X - self.X;
				b = self.thread_list[self.target_id].Y - self.Y;

				self.compute_trajectory(a, b, TARGET_KIND);


		
		# The drone destroyed the ennemi and is destroy too	
		if self.thread_list[self.target_id].state_thread == "ON" and self.in_diameter(int(self.X), int(self.thread_list[self.target_id].X)) and self.in_diameter(int(self.Y), int(self.thread_list[self.target_id].Y)) and self.in_height(int(self.Z), int(self.thread_list[self.target_id].Z)) and g.CONTINUE:
			self.state = drone_out;
			self.thread_list[self.target_id].thread_state = "OFF";
			self.thread_list[self.target_id].state = drone_out;
			self.label.config(bg="red", text="DRONE "+str(self.id+1)+"\nDestroyed");
		# The ennemi is destroyed but the drone is still OK
		elif self.thread_list[self.target_id].state_thread == "ON" and g.CONTINUE:
			print ("Ennemi ESCAPED")
			self.thread_list[self.target_id].state = drone_ennemi_escaped;


		self.comingback_phase();
		
		
	def run(self):

		if g.CONTINUE:
			print ("---- START MOVE : "+str(self.kind)+" - "+str(self.id)+ " ----\n");

		self.drone_movement();

		if g.CONTINUE:
			if self.state == drone_out: 
				print ("---- END MOVE : "+str(self.kind)+" - "+str(self.id)+ " -> DESTROYED ----\n");
			elif self.state == drone_back:
				print ("---- END MOVE : "+str(self.kind)+" - "+str(self.id)+ " -> BACK ----\n");
			else: 
				print ("---- END MOVE : "+str(self.kind)+" - "+str(self.id)+ " -> ESCAPED ----\n")
			




