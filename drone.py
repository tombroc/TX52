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

time_sleep           = 0.01;
loop_number          = 1;

drone_out            = 0;
drone_ready          = 2;
drone_flying         = 3;
drone_back           = 4;	# Drone back of a mission ready for inspection
drone_ennemi_ready   = 7;
drone_ennemi_escaped = 8;

class Drone(Thread):

	def __init__(self, kind, identifier, CANVAS_C, X, Y, Z, ennemi_list, drone_list, label):
		Thread.__init__(self);
		drone_ready        = 2;	# Drone on his spot and operational
		drone_ennemi_ready = 7;	# Drone ennemi ready
		
		self.canvas        = CANVAS_C;
		self.id            = identifier;
		self.kind          = kind;
		self.diameter      = 20;
		self.height        = 5;
		self.X             = X;
		self.Y             = Y;
		self.Z             = Z;
		self.label         = label;
		self.event         = Event();
		
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
		self.drone_list    = drone_list;
		self.ennemi_list   = ennemi_list;

	# Tell the drone to go straight
	def go_straight(self, dY):
		return self.Y - dY;

	# 
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

		a = a / sqrt(a**2 + b**2);
		b = b / sqrt(a**2 + b**2);

		# Parameter t

		t = (self.speed)#* sqrt(1/(a**2 + b**2 + c**2)));

		# New coordinnates for the drone (using parametric system)

		newX = self.go_right(t * a);
		newY = self.go_back(t * b);
		newZ = self.Z;

		# Target is an ennemi
		if TARGET_KIND == 0:
			if self.ennemi_list and self.ennemi_list[0].Z > self.Z:
				newZ = self.Z + 1;
			elif self.ennemi_list and self.ennemi_list[0].Z < self.Z:
				newZ = self.Z - 1;

		# Target is QG
		# Stop 10meters above the QG spot
		elif self.Z > self.Z_SPOT + 10:
			newZ = 0.9 * self.Z;
			

		if self.check_trajectory(newX, newY, newZ):

			self.canvas.move(self.drone, t * a, t * b);
			self.canvas.move(self.alt_t, t * a, t * b);
			self.canvas.move(self.name_t, t * a, t * b);

		self.canvas.itemconfig(self.alt_t, text="Alt : "+str(int(newZ))+"m");
		self.canvas.update();

		# Update of the drone coordinates

		self.X = newX;
		self.Y = newY;
		self.Z = newZ;

	def check_trajectory(self, X, Y, Z):
		dX = 1;
		for ally in self.drone_list:
			if ally.id != self.id and ally.state == drone_flying:
				dist = sqrt( (X - ally.X)**2 + (Y - ally.Y)**2);
				#print ("dist = " +str(dist)+ " diameter = "+str(self.diameter))
				if  dist <= self.diameter + 2 and X < ally.X:
					#print ("---- Trajectory correction : "+str(self.kind)+" - "+str(self.id) +" ----\n");
					# The drone must change his trajectory
					self.canvas.move(self.drone,  (X-self.X)*2, (Y-self.Y)/2);
					self.canvas.move(self.alt_t,  (X-self.X)*2, (Y-self.Y)/2);
					self.canvas.move(self.name_t, (X-self.X)*2, (Y-self.Y)/2);
					self.canvas.update();
					self.Y = self.go_straight((Y-self.Y)/2);
					if X < ally.X:
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
		print ("slowing down drone "+str(self.kind)+" "+str(self.id))
		COEFF_SLOW_DOWN = 0.05 * self.speed_max;
		if self.speed - COEFF_SLOW_DOWN >= speed:
			self.speed = self.speed - COEFF_SLOW_DOWN;

	def acceleration_phase(self):
		print ("acceleration drone "+str(self.kind)+" "+str(self.id))
		COEFF_ACCELERATION = 0.05 * self.speed_max;
		if self.speed + COEFF_ACCELERATION <= self.speed_max:
			self.speed = self.speed + COEFF_ACCELERATION;

	def takeoff_phase(self):
		if self.ennemi_list[0].Z > 8:
			while self.ennemi_list and self.Z < 10 and g.CONTINUE:
				self.thread_traitment();
				if self.Z > self.ennemi_list[0].Z:
					self.Z = self.Z - 1;
				elif self.Z < self.ennemi_list[0].Z:
					self.Z = self.Z + 1;
				self.canvas.itemconfig(self.alt_t, text="Alt : "+str(int(self.Z))+"m");
				self.canvas.update();
		else:
			while self.ennemi_list and not self.between(self.Z, self.ennemi_list[0].Z, 2) and g.CONTINUE:
				self.thread_traitment();
				if self.Z > self.ennemi_list[0].Z:
					self.Z = self.Z - 1;
				elif self.Z < self.ennemi_list[0].Z:
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
				time.sleep(time_sleep);

	def Uturn_phase(self, phase):
		print ("slowing down drone "+str(self.kind)+" "+str(self.id))
		if phase == 1:
			while int(self.speed) > 0:
				print (self.speed)
				self.slowing_down_phase(0);
			self.speed = 0;
		elif phase == 2:
			while round(self.speed, 1) < self.speed_max:
				print (round(self.speed, 1))
				self.acceleration_phase();


	def thread_traitment(self):
	
		if self.kind == 'ally':
			i = self.id+1;
			test = True;
			while(i < g.NUMBER_DRONE and test):
				if self.drone_list[i].state == drone_flying:
					self.drone_list[i].event.clear();
					self.drone_list[i].event.set();
					test = False;
					kind = "ally";
				i = i + 1;
			i = 0;
			while(i < len(self.ennemi_list) and test):
				if self.ennemi_list[i].state == drone_ennemi_ready:
					self.ennemi_list[i].event.clear();
					self.ennemi_list[i].event.set();
					test = False;
					kind = "ennemi";
				i = i + 1;

			time.sleep(time_sleep);
			
			if not test:
				# We have to stop the current thread as a last resort to be sure it can stop all the other thread first
				for ally in self.drone_list:
					if (kind != ally.kind or i != ally.id) and (ally.id != self.id or self.kind != ally.kind):
						ally.event.wait();
				for ennemi in self.ennemi_list:
					if (kind != ennemi.kind or i != ally.id) and (ennemi.id != self.id or self.kind != ennemi.kind):
						ennemi.event.wait();
				self.event.wait();

		elif self.kind == "ennemi":
			i = self.id+1;
			test = True;
			while(i < len(self.ennemi_list) and test):
				if self.ennemi_list[i].state == drone_ennemi_ready:
					self.ennemi_list[i].event.clear();
					self.ennemi_list[i].event.set();
					test = False;
					kind = "ennemi";
				i = i + 1;
			i = 0;

			while(i < g.NUMBER_DRONE and test):
				if self.drone_list[i].state == drone_flying:
					self.drone_list[i].event.clear();
					self.drone_list[i].event.set();
					test = False;
					kind = "ally";
				i = i + 1;
			time.sleep(time_sleep);

			if not test:
				# We have to stop the current thread as a last resort to be sure it can stop all the other thread first
				for ennemi in self.ennemi_list:
					if (kind != ennemi.kind or i != ally.id) and (ennemi.id != self.id or self.kind != ennemi.kind):
						ennemi.event.wait();
				for ally in self.drone_list:
					if (kind != ally.kind or i != ally.id) and (ally.id != self.id or self.kind != ally.kind):
						ally.event.wait();
				self.event.wait();

	def drone_movement(self):
		

		#i = 0;
		TARGET_KIND = 0;
		# Takeoff phase
		self.takeoff_phase();
		#time.sleep(5);
		while (self.ennemi_list and (self.out_diameter(int(self.X), int(self.ennemi_list[0].X)) 
			or self.out_diameter(int(self.Y), int(self.ennemi_list[0].Y)) 
			or self.out_height(self.Z, self.ennemi_list[0].Z))
			and sqrt((self.ennemi_list[0].X - (g.WIDTH_CANVAS)/2) * (self.ennemi_list[0].X - (g.WIDTH_CANVAS)/2) + (self.ennemi_list[0].Y - (g.HEIGHT_CANVAS)) * (self.ennemi_list[0].Y - (g.HEIGHT_CANVAS))) <= g.VIRTUAL_SCOPE+15) and g.CONTINUE:
			

			#print ("Thread id : "+ str(self.id)+ " Kind : "+str(self.kind));
			self.thread_traitment();
			self.acceleration_phase();
			# Best trajectory to intercept the intruder

			# Direction vector between drone and ennemi
			if self.ennemi_list:
				a = self.ennemi_list[0].X - self.X;
				b = self.ennemi_list[0].Y - self.Y;

				self.compute_trajectory(a, b, TARGET_KIND);

		
		# The drone destroyed the ennemi and is destroy too	
		if self.ennemi_list and self.in_diameter(int(self.X), int(self.ennemi_list[0].X)) and self.in_diameter(int(self.Y), int(self.ennemi_list[0].Y)) and self.in_height(int(self.Z), int(self.ennemi_list[0].Z)) and g.CONTINUE:
			self.state = drone_out;
			self.ennemi_list[0].state = drone_out;
			self.label.config(bg="red", text="DRONE "+str(self.id+1)+"\nDestroyed");
		# The ennemi is destroyed but the drone is still OK
		elif self.ennemi_list and g.CONTINUE:
			print ("ESCAPED")
			self.ennemi_list[0].state = drone_ennemi_escaped;



		#------ Back to GQ if the ennemi escaped or if another drone intersepted it ------#
		TARGET_KIND = 1;
		if ((self.ennemi_list and self.state == drone_flying and (self.ennemi_list[0].state == drone_ennemi_escaped)) or ((not self.ennemi_list) and self.state == drone_flying)) and g.CONTINUE:
			self.Uturn_phase(1);
			#print ("In if")
			i = 0;
			self.label.config(text="DRONE "+str(self.id+1)+"\nComing back");
			count = 0;
			slow_counter = 0;
			self.Uturn_phase(2);
			while (self.out_diameter(self.X, self.X_SPOT) 
				or self.out_diameter(self.Y, self.Y_SPOT)) and g.CONTINUE:
				
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
				if self.ennemi_list:
					self.ennemi_list[0].state = drone_out;
		

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
			




