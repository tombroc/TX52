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
drone_ennemi_detected = 6;	# Drone ennemi detected
drone_ennemi_ready   = 7;
drone_ennemi_escaped = 8;

class Drone(Thread):

	def __init__(self, utils, CANVAS_C, Id, X, Y, Z, thread_list, label):
		Thread.__init__(self);
		
		self.canvas               = CANVAS_C;
		self.id                   = Id;
		self.kind                 = "ally";
		self.real_diameter        = 0.5; # in meter
		self.simulation_diameter  = self.real_diameter * g.DIMENSION_COEFFICIENT * 10;
		self.real_height          = 0.2;
		self.X                    = X;
		self.Y                    = Y;
		self.Z                    = Z;
		self.dX                   = 0.0;
		self.dY                   = 0.0;
		self.dZ                   = 0.0;
		self.label                = label;
		self.event                = Event();
		self.acceleration_coeff   = 0.02; # In %
		self.deceleration_coeff   = 0.02; # In %
		self.event.set();	
		tags                      = "drone";
		color                     = "blue";
		position                  = "ne"
		offset                    = -self.simulation_diameter-15;
		self.speed                = 0;
		self.real_speed_max       = 11; # In meter/s 
		self.simulation_speed_max = self.real_speed_max * g.DIMENSION_COEFFICIENT / 10; 
		self.name_t               = CANVAS_C.create_text(self.X, self.Y+30, anchor="s", text="Drone "+str(self.id+1), tags="text", fill=color);
		self.X_SPOT               = X;
		self.Y_SPOT               = Y;
		self.Z_SPOT               = Z;
		
		alt                       = "Alt : "+ str(self.Z) +"m";
		self.drone                = CANVAS_C.create_polygon(self.X, self.Y, self.X+self.simulation_diameter+5, self.Y+self.simulation_diameter+5, self.X, self.Y+self.simulation_diameter+2.5, self.X-self.simulation_diameter-5, self.Y+self.simulation_diameter+5, tags=tags, fill=color);
		self.alt_t                = CANVAS_C.create_text(self.X, self.Y+45, anchor="s", text=alt, tags="alt", fill=color);
		self.state                = drone_ready;
		self.state_thread         = "OFF";
		self.thread_list          = thread_list;
		self.target               = -1;

		self.utils                = utils;
	# Tell the drone to go straight
	def go_straight(self):
		return self.Y + self.dY;

	def go_back(self):
		return self.Y + self.dY;

	def go_right(self):
		return self.X + self.dX;

	def go_left(self):
		return self.X + self.dX;

	def go_up(self):
		return self.Z + self.dZ;

	def go_down(self):
		return self.Z - self.dZ;

	def get_coords(self):
		return self.X, self.Y, self.Z;
	
	def abs(self, a):
		if a > 0:
			return a;
		else:
			return -a;

	def out_diameter(self, X, a):
		if a-self.simulation_diameter/2 <= X <= a+self.simulation_diameter/2:
			return False;
		else:
			return True;

	def in_diameter(self, X, a):
		if a-self.simulation_diameter/2 <= X <= a+self.simulation_diameter/2:
			return True;
		else:
			return False;

	def out_height(self, X, a):
		if a-self.real_height/2 <= X <= a+self.real_height/2:
			return False;
		else:
			return True;

	def in_height(self, X, a):
		if a-self.real_height/2 <= X <= a+self.real_height/2:
			return True;
		else:
			return False;

	def between(self, X, Y, a):
		if X > Y-a and X < Y+a:
			return True;
		else:
			return False;

	def stop_Movment(self):
		self.dX = 0;
		self.dY = 0;
		self.dZ = 0;

	def slowing_down_phase(self, speed):
		COEFF_SLOW_DOWN = self.deceleration_coeff * self.simulation_speed_max;
		if self.speed - COEFF_SLOW_DOWN >= speed * g.DIMENSION_COEFFICIENT:
			self.speed = self.speed - COEFF_SLOW_DOWN;

	def acceleration_phase(self):
		COEFF_ACCELERATION = self.acceleration_coeff * self.simulation_speed_max;
		if round(self.speed + COEFF_ACCELERATION, 1) <= self.simulation_speed_max:
			self.speed = self.speed + COEFF_ACCELERATION;

	def takeoff_phase(self):
		if self.target.Z > 8:
			while self.target.state_thread == "ON" and self.target and self.Z < 10 and g.CONTINUE:
				self.utils.thread_traitment(True, self.thread_list.index(self));
				if self.Z > self.target.Z:
					self.Z = self.Z - 1;
				elif self.Z < self.target.Z:
					self.Z = self.Z + 1;
		else:
			while self.target.state_thread == "ON" and not self.between(self.Z, self.target.Z, 2) and g.CONTINUE:
				self.utils.thread_traitment(True, self.thread_list.index(self));
				if self.Z > self.target.Z:
					self.dZ = -1;
				elif self.Z < self.target.Z:
					self.dZ = 1;
				self.Z = self.Z + self.dZ;

	def landing_phase(self):
		# Go down until the drone touch the ground

		self.label.config(text="DRONE "+str(self.id+1)+"\nComing back\n"+str(round(self.speed / g.DIMENSION_COEFFICIENT * 10, 1))+"m/s");
		while self.Z > self.Z_SPOT and g.CONTINUE:
			self.utils.thread_traitment(True, self.thread_list.index(self));
			self.Z -= 0.1;
			#time.sleep(g.time_sleep);

	def Uturn_phase(self, phase):
		#print ("slowing down drone "+str(self.kind)+" "+str(self.id+1))
		if phase == 1:
			while int(self.speed) > 0:
				self.utils.thread_traitment(True, self.thread_list.index(self));
				self.slowing_down_phase(0);
				#print ("Uturn_phase 1")
			self.speed = 0;
		elif phase == 2:
			while round(self.speed, 1) < self.simulation_speed_max:
				self.utils.thread_traitment(True, self.thread_list.index(self));
				self.acceleration_phase();
				#print ("Uturn_phase 2 : "+str(self.speed))

	def comingback_phase(self):
		print ("Start coming back phase - "+str(self.id));
		#------ Back to GQ if the ennemi escaped or if another drone intersepted it ------#
		TARGET_KIND = 1;
		if self.state == drone_flying and g.CONTINUE:
			#self.Uturn_phase(1);
			
			i = 0;
			self.label.config(text="DRONE "+str(self.id)+"\nComing back");
			count = 0;
			#self.Uturn_phase(2);
			while (self.out_diameter(self.X, self.X_SPOT)
				or self.out_diameter(self.Y, self.Y_SPOT)) and g.CONTINUE:
				
				self.utils.thread_traitment(True, self.thread_list.index(self));

				if (self.abs(self.X-self.X_SPOT) < 10 * g.DIMENSION_COEFFICIENT or self.abs(self.Y-self.Y_SPOT) < 10 * g.DIMENSION_COEFFICIENT):
					self.slowing_down_phase(5);
				elif (self.abs(self.X-self.X_SPOT) < 25 * g.DIMENSION_COEFFICIENT and self.abs(self.Y-self.Y_SPOT) < 25 * g.DIMENSION_COEFFICIENT):
					self.slowing_down_phase(5);
				

				a = self.X_SPOT - self.X;
				b = self.Y_SPOT - self.Y;

				#print ("a = "+str(a)+" b = "+str(b)+" c = "+str(c));
				self.compute_trajectory(a, b, TARGET_KIND);
				#print (str(self.kind)+" "+str(self.id)+"\tself.dX = "+str(self.dX)+"\tself.dY = "+str(self.dY)+"\tself.state_thread = "+str(self.state_thread))
			
			self.stop_Movment();

			print("Drone "+str(self.id)+" - Landing phase")
			self.slowing_down_phase(0);
			self.landing_phase();
				
			if g.CONTINUE:
				self.state = drone_back;	# Drone back of a mission ready for inspection
				self.label.config(bg="blue", text="DRONE "+str(self.id+1)+"\nBack");
				# if the ennemi escaped we get him out of the list
				if self.target.state_thread == "ON":
					self.target.state = drone_out;
			self.state_thread = "OFF";

	def check_trajectory(self, newX, newY, newZ):
		#self.dX = 1;
		for thread in self.thread_list:
			if thread.kind == "ally" and thread.id != self.id and thread.state == drone_flying:
				dist = sqrt( (newX - thread.X)**2 + (newY - thread.Y)**2);
				if  dist <= self.simulation_diameter * 2 and self.in_height(newZ, thread.Z) :
					print ("Correction trajectory on")
					if newY > thread.Y:
						print ("---- Trajectory correction : "+str(self.kind)+" - "+str(self.id) +" ----\n");
						# The drone must change his trajectory
			
						# Direction : Canvas' top
						if self.dY < 0:
							self.slowing_down_phase(1); 

					elif newY < thread.Y:
						print ("---- Trajectory correction : "+str(self.kind)+" - "+str(self.id) +" ----\n");
						# The drone must change his trajectory
						# Direction : Canvas' bottom
						if self.dY > 0:
							self.slowing_down_phase(1);

					if newX > thread.X:
						print ("---- Trajectory correction : "+str(self.kind)+" - "+str(self.id) +" ----\n");
						# The drone must change his trajectory

						# Direction : Canvas' top
						if self.dX < 0:
							self.slowing_down_phase(1); 

					elif newX < thread.X:
						print ("---- Trajectory correction : "+str(self.kind)+" - "+str(self.id) +" ----\n");
						# The drone must change his trajectory
						# Direction : Canvas' bottom
						if self.dX > 0:
							self.slowing_down_phase(1);
		
					value = False;
				else:
					value = True;
			else:
				# No other drone flying
				value = True;
		return value; 

	def compute_trajectory(self, a, b, TARGET_KIND):

		# Unitary vector
		
		newa = a / sqrt(a**2 + b**2);
		newb = b / sqrt(a**2 + b**2);
		
		# Parameter t

		t = self.speed;
		#print ("self.speed = "+str(self.speed)+"newa = "+str(newa))
		# New coordinnates for the drone (using parametric system)
		self.dX = t * newa;
		#print ("Thread id = "+str(self.id)+" dX = " +str(self.dX))
		if self.dX > 0:
			newX = self.go_right();
		else:
			newX = self.go_left();

		self.dY = t * newb;
		if self.dY > 0:
			newY = self.go_back();
		else:
			newY = self.go_straight();

		self.dZ = 1;
		newZ = self.Z;

		# Computing of the optimal trajectory
		# Correction of it if necessary

		# Target is an ennemi
		if TARGET_KIND == 0:
			self.label.config(text="DRONE "+str(self.id+1)+"\nIn mission\n"+str(round(self.speed / g.DIMENSION_COEFFICIENT * 10, 1))+"m/s");
			self.acceleration_phase();
			if self.target.state_thread == "ON" and self.target.Z > self.Z:
				self.dZ = 1;
				newZ = self.go_up();
			elif self.target.state_thread == "ON" and self.target.Z < self.Z:
				self.dZ = -1;
				newZ = self.go_down();

		# Target is QG
		# Stop 10meters above the QG spot
		elif TARGET_KIND == 1 :
			self.label.config(text="DRONE "+str(self.id+1)+"\nComing back\n"+str(round(self.speed / g.DIMENSION_COEFFICIENT * 10, 1))+"m/s");
			if self.Z >= self.Z_SPOT + 11:	
				self.dZ = 0.05 * self.Z
				newZ = self.go_down();

		current_speed = self.speed;
		if not self.check_trajectory(newX, newY, newZ):
			print ("check trajectory false")
			if TARGET_KIND == 0:
				self.label.config(text="DRONE "+str(self.id+1)+"\nIn mission\n"+str(round(self.speed / g.DIMENSION_COEFFICIENT * 10, 1))+"m/s");
			else: 
				self.label.config(text="DRONE "+str(self.id+1)+"\nComing back\n"+str(round(self.speed / g.DIMENSION_COEFFICIENT * 10, 1))+"m/s");

			# Parameter t
			t = self.speed;
			# New coordinnates for the drone (using parametric system)
			self.dX = t * newa;
			if self.dX > 0:
				newX = self.go_right();
			else:
				newX = self.go_left();

			self.dY = t * newb;
			if self.dY > 0:
				newY = self.go_back();
			else:
				newY = self.go_straight();

			# self.speed has been changed in the check_trajectory function : we put it back like before
			self.speed = current_speed;
		# Update of the drone coordinates

		self.X = newX;
		self.Y = newY;
		self.Z = newZ;

	def drone_movement(self):
		self.event.set();
		self.event.clear();
		self.event.wait();
		#i = 0;
		TARGET_KIND = 0;
		# Takeoff phase
		self.takeoff_phase();

		while (self.thread_list[self.thread_list.index(self.target)].state_thread == "ON" and self.thread_list[self.thread_list.index(self.target)].state != drone_out and (self.out_diameter(int(self.X), int(self.target.X)) 
			or self.out_diameter(int(self.Y), int(self.target.Y - self.target.simulation_diameter/2)) 
			or self.out_height(self.Z, self.target.Z))
			and sqrt((self.target.X - (g.WIDTH_CANVAS)/2) * (self.target.X - (g.WIDTH_CANVAS)/2) + (self.target.Y - (g.HEIGHT_CANVAS)) * (self.target.Y - (g.HEIGHT_CANVAS))) <= g.VIRTUAL_SCOPE+15) and g.CONTINUE:
			
			self.utils.thread_traitment(True, self.thread_list.index(self));
			# Best trajectory to intercept the intruder

			# Direction vector between drone and ennemi
			if self.target.state_thread == "ON":
				# Calculation of the directory vector
				a = self.target.X - self.X;
				b = self.target.Y - self.Y;

				self.compute_trajectory(a, b, TARGET_KIND);
		
		# The drone destroyed the ennemi and is destroy too	
		if self.target.state != drone_out and self.in_diameter(int(self.X), int(self.target.X)) and self.in_diameter(int(self.Y), int(self.target.Y) - self.target.simulation_diameter/2) and self.in_height(int(self.Z), int(self.target.Z)) and g.CONTINUE:
			print ("ENNEMI DOWN "+str(self.target.id)+" - ALLY DOWN")
			self.state = drone_out;
			self.state_thread = "OFF";
			# Also done in the radar thread but for the synchronization we need to do it right now
			self.thread_list[self.thread_list.index(self.target)].state = drone_out;
			self.label.config(bg="red", text="DRONE "+str(self.id+1)+"\nDestroyed");

		# The ennemi is destroyed but the drone is still OK
		elif self.target.state != drone_out and sqrt(
														(self.X - (g.WIDTH_CANVAS)/2) * (self.X - (g.WIDTH_CANVAS)/2) 
													  + (self.Y - (g.HEIGHT_CANVAS)) * (self.Y - (g.HEIGHT_CANVAS))
													) > g.VIRTUAL_SCOPE and g.CONTINUE:
			print ("Ennemi ESCAPED "+str(self.target.id)+" - ALLY ALIVE");
			self.thread_list[self.thread_list.index(self.target)].state = drone_ennemi_escaped;
			self.comingback_phase();
		
		else:
			print ("Ennemi DOWN "+str(self.target.id)+" - ALLY COMMING BACK")
			self.comingback_phase();
		print (self.target.state);

		if g.CONTINUE:
			# Here the thread has to set the next one but not sleep because it's his las action and he is going to come to the end
			self.stop_Movment();
			self.utils.thread_traitment(False, self.thread_list.index(self));
		
	def run(self):

		if g.CONTINUE:
			print ("---- START MOVE : "+str(self.kind)+" - "+str(self.id)+ " ----\n");

		self.drone_movement();

		if g.CONTINUE:
			if self.state == drone_out: 
				print ("---- END MOVE : "+str(self.kind)+" - "+str(self.thread_list.index(self))+ " -> DESTROYED ----\n");
			elif self.state == drone_back:
				print ("---- END MOVE : "+str(self.kind)+" - "+str(self.thread_list.index(self))+ " -> BACK ----\n");
			else: 
				print ("---- END MOVE : "+str(self.kind)+" - "+str(self.thread_list.index(self))+ " -> ESCAPED ----\n")
			




