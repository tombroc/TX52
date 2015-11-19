#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*-iso-8859-15 -*
import os
import graphics as g
from tkinter import *
from threading import Thread, RLock, Event
from math import sqrt
import time
import random

drone_event = Event();
ennemi_event = Event();
drone_event.set();
ennemi_event.set();

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
		drone_ready          = 2;	# Drone on his spot and operational
		drone_ennemi_ready   = 7;	# Drone ennemi ready
		
		self.canvas          = CANVAS_C;
		self.id              = identifier;
		self.kind            = kind;
		self.diameter        = 20;
		self.height          = 5;
		self.X               = X;
		self.Y               = Y;
		self.Z               = Z;
		self.label           = label;
		self.event           = Event();

		self.event.set();	
			
		if kind == "ennemi":
			tags             = "ennemi_";
			color            = "black";
			position         = "nw"
			state            = drone_ennemi_ready;
			offset 			 = self.diameter;

		else:
			tags             = "drone_";
			color            = "blue";
			position         = "ne"
			state            = drone_ready;
			offset 			 = -self.diameter;
			self.speed       = 3;
			self.name_t      = CANVAS_C.create_text(self.X, self.Y+self.diameter+20, anchor="s", text="Drone "+str(self.id+1), tags="drone_"+ str(self.kind)+"_"+str(self.id+1), fill=color);
			self.X_SPOT      = X;
			self.Y_SPOT      = Y;
			self.Z_SPOT      = Z;
			
		alt                  = "Alt : "+ str(self.Z) +"m";
		self.drone           = CANVAS_C.create_polygon(self.X, self.Y, self.X+self.diameter, self.Y+self.diameter, self.X-self.diameter, self.Y+self.diameter, tags=tags+str(self.id), fill=color);
		self.alt_t           = CANVAS_C.create_text(self.X+offset, self.Y+2, anchor=position, text=alt, tags="alt_"+ str(self.kind)+"_"+str(self.id+1), fill=color);
		self.state           = state;
		self.drone_list      = drone_list;
		self.ennemi_list     = ennemi_list;


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

	def compute_trajectory(self, a, b, c):

		# Unitary vector

		a = a / sqrt(a**2 + b**2 + c**2);
		b = b / sqrt(a**2 + b**2 + c**2);
		c = c / sqrt(a**2 + b**2 + c**2);

		# Parameter t

		t = (self.speed)#* sqrt(1/(a**2 + b**2 + c**2)));

		# New coordinnates for the drone (using parametric system)

		newX = self.X + t * a;
		newY = self.Y + t * b;
		newZ = self.Z + t * c;
		
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
				if  dist <= self.diameter:# and (self.Z + dZ) == ally.Z :
					print ("---- Trajectory correction : "+str(self.kind)+" - "+str(self.id) +" ----\n");
					# The drone must change his trajectory
					self.canvas.move(self.drone,  (X-self.X)*2, (Y-self.Y)/2);
					self.canvas.move(self.alt_t,  (X-self.X)*2, (Y-self.Y)/2);
					self.canvas.move(self.name_t, (X-self.X)*2, (Y-self.Y)/2);
					self.Y = self.go_straight((Y-self.Y)/2);
					if X < ally.X:
						self.X = self.go_left((X-self.X)*2);
					else: 
						self.X = self.go_right((X-self.X)*2);
					return False;
				else:
					return True;
			else:
				# No other drone flying
				return True; 

	def slowing_down_phase(self):

		if self.speed >= 1:
			COEFF_SLOW_DOWN = 0.5;
			self.speed = self.speed - COEFF_SLOW_DOWN;
		print ("Slowing down");

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

	def ennemi_movement(self):

		dY = 1;
		newX = 0.0;
		newY = 0.0;
		newZ = 0.0;
		
		while sqrt(
						(self.X - (g.WIDTH_CANVAS)/2) * (self.X - (g.WIDTH_CANVAS)/2) 
					  + (self.Y - (g.HEIGHT_CANVAS)) * (self.Y - (g.HEIGHT_CANVAS))
					) > g.VIRTUAL_SCOPE and g.CONTINUE:
			#print ("Thread id : "+ str(self.id)+ " Kind : "+str(self.kind));
			self.thread_traitment();

			if self.X <= g.WIDTH_CANVAS/2:
				a = -1;
				b = 2;
				dX = random.uniform(a, b);
			elif self.X > g.WIDTH_CANVAS/2:
				a = -2;
				b = 1;
				dX = random.uniform(a, b);

			if self.Z < 3:
				dZ = 2;
			else:
				dZ = random.randint(-1,1);

			self.X = self.X + dX;
			self.Y = self.Y + dY;
			self.Z = self.Z + dZ;

			self.canvas.move(self.drone, dX, dY);
			self.canvas.move(self.alt_t, dX, dY);
			self.canvas.itemconfig(self.alt_t, text="Alt : "+str(int(self.Z))+"m");
			self.canvas.update();
		i = 0;

		while self.state != drone_out and self.Y < g.HEIGHT_CANVAS+10 and g.CONTINUE:
			#if i == loop_number:
				#i = 0;
			#print ("Thread id : "+ str(self.id)+ " Kind : "+str(self.kind));
			self.thread_traitment();

			if self.X > g.WIDTH_CANVAS - 50   and self.X < g.WIDTH_CANVAS and dX > 0:
				dX = random.randint(-1,1);
			elif self.X > g.WIDTH_CANVAS - 50 and self.X < g.WIDTH_CANVAS:
				dX = -1;
			elif self.X < 50 and self.X > 0   and dX < 0:
				dX = random.randint(-1,1);
			elif self.X > g.WIDTH_CANVAS - 50 and self.X < g.WIDTH_CANVAS:
				dX = 1;
			elif i == 0:
				 dX = random.randint(-2,2);

			if (self.Y >= (g.HEIGHT_CANVAS-g.VIRTUAL_SCOPE) and dY > 0) or self.Y < 0:
				dY = 1;
			else:
				dY = -1;
			dZ = 0;

			self.X += dX;
			self.Y += dY;
			self.Z += dZ;

			self.canvas.move(self.drone, dX, dY);
			self.canvas.move(self.alt_t, dX, dY);
			self.canvas.itemconfig(self.alt_t, text="Alt : "+str(int(self.Z))+"m");
			self.canvas.update();
			i = 1;

	def drone_movement(self):
		

		#i = 0;
		while (self.ennemi_list and (self.out_diameter(int(self.X), int(self.ennemi_list[0].X)) 
			or self.out_diameter(int(self.Y), int(self.ennemi_list[0].Y)) 
			or self.out_height(self.Z, self.ennemi_list[0].Z))
			and sqrt((self.ennemi_list[0].X - (g.WIDTH_CANVAS)/2) * (self.ennemi_list[0].X - (g.WIDTH_CANVAS)/2) + (self.ennemi_list[0].Y - (g.HEIGHT_CANVAS)) * (self.ennemi_list[0].Y - (g.HEIGHT_CANVAS))) <= g.VIRTUAL_SCOPE+15) and g.CONTINUE:
			
			print ("Thread id : "+ str(self.id)+ " Kind : "+str(self.kind));
			self.thread_traitment();
			
			# Best trajectory to intercept the intruder

			# Direction vector between drone and ennemi
			if self.ennemi_list:
				a = self.ennemi_list[0].X - self.X;
				b = self.ennemi_list[0].Y - self.Y;
				c = self.ennemi_list[0].Z - self.Z;


				self.compute_trajectory(a, b, c);

		
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

		if ((self.ennemi_list and self.state == drone_flying and (self.ennemi_list[0].state == drone_ennemi_escaped)) or ((not self.ennemi_list) and self.state == drone_flying)) and g.CONTINUE:
			#print ("In if")
			i = 0;
			self.label.config(text="DRONE "+str(self.id+1)+"\nComing back");
			
			while (self.out_diameter(self.X, self.X_SPOT) 
				or self.out_diameter(self.Y, self.Y_SPOT) 
				or self.out_height(self.Z, self.Z_SPOT)) and g.CONTINUE:
				
				# i += 1;
				# if i == loop_number and self.ennemi_list:
				# 	i = 0;
				self.thread_traitment();
				
				if sqrt((self.X-self.X_SPOT)**2 + (self.Y-self.Y_SPOT)**2) < 100:
					self.slowing_down_phase();

				a = self.X_SPOT - self.X;
				b = self.Y_SPOT - self.Y;
				c = 2 - self.Z;

				print ("X = "+str(self.X)+" Y = "+str(self.Y)+" Z = "+str(self.Z));
				#print ("a = "+str(a)+" b = "+str(b)+" c = "+str(c));
				self.compute_trajectory(a, b, c);

			# Go down until the drone touch the ground
			while self.Z > self.Z_SPOT:
				self.thread_traitment();
				self.Z -= 0.1;
				self.canvas.itemconfig(self.alt_t, text="Alt : "+str(int(self.Z))+"m");
				self.canvas.update();
				time.sleep(time_sleep);
				


			if g.CONTINUE:
				self.state = drone_back;	# Drone back of a mission ready for inspection
				self.label.config(bg="blue", text="DRONE "+str(self.id+1)+"\nBack");
				# if the ennemi escaped we get him out of the list
				if self.ennemi_list:
					self.ennemi_list[0].state = drone_out;
		

	def run(self):

		if g.CONTINUE:
			print ("---- START MOVE : "+str(self.kind)+" - "+str(self.id)+ " ----\n");

		if self.kind == "ennemi":
			self.ennemi_movement();
		elif self.kind == "ally":
			self.drone_movement();

		if g.CONTINUE:
			if self.state == drone_out: 
				print ("---- END MOVE : "+str(self.kind)+" - "+str(self.id)+ " -> DESTROYED ----\n");
			elif self.state == drone_back:
				print ("---- END MOVE : "+str(self.kind)+" - "+str(self.id)+ " -> BACK ----\n");
			else: 
				print ("---- END MOVE : "+str(self.kind)+" - "+str(self.id)+ " -> ESCAPED ----\n")
			




