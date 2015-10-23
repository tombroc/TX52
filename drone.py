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

t = 0.001;
loop_number  = 1;

drone_out    = 0;
drone_ready  = 2;
drone_flying = 3;
drone_back   = 4;	# Drone back of a mission ready for inspection
drone_ennemi_ready = 7;
drone_ennemi_escaped  = 8;

class Drone(Thread):

	def __init__(self, kind, identifier, CANVAS_C, X, Y, Z, ennemi_list, label):
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
			
			
		if kind == "ennemi":
			tags             = "ennemi_";
			color            = "black";
			position         = "nw"
			state            = drone_ennemi_ready;
		else:
			tags             = "drone_";
			color            = "blue";
			position         = "nw"
			state            = drone_ready;
			self.ennemi_list = ennemi_list;
			self.name_t      = CANVAS_C.create_text(self.X, self.Y+self.diameter+20, anchor="s", text="Drone "+str(self.id+1), tags="drone_"+ str(self.kind)+"_"+str(self.id+1), fill=color);	
			
		alt                  = "Alt : "+ str(self.Z) +"m";
		self.drone           = CANVAS_C.create_polygon(self.X, self.Y, self.X+self.diameter, self.Y+self.diameter, self.X-self.diameter, self.Y+self.diameter, tags=tags+str(self.id), fill=color);
		self.alt_t           = CANVAS_C.create_text(self.X+self.diameter, self.Y+2, anchor=position, text=alt, tags="alt_"+ str(self.kind)+"_"+str(self.id+1), fill=color);
		self.state           = state;

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
		if a-self.diameter/2 <= X <= a+self.diameter:
			return False;
		else:
			return True;

	def in_diameter(self, X, a):
		if a-self.diameter/2 <= X <= a+self.diameter:
			return True;
		else:
			return False;

	def ennemi_movement(self):
		dY = 1;
		newX = 0.0;
		newY = 0.0;
		newZ = 0.0;
		
		print ("---- MOVE : Ennemi ----");
		while sqrt(
						(self.X - (g.WIDTH_CANVAS)/2) * (self.X - (g.WIDTH_CANVAS)/2) 
					  + (self.Y - (g.HEIGHT_CANVAS)) * (self.Y - (g.HEIGHT_CANVAS))
					) > g.VIRTUAL_SCOPE and g.CONTINUE:

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
			drone_event.clear();
			drone_event.set();
			time.sleep(t);
			ennemi_event.wait();

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

		print ("---- END MOVE : Ennemi----");

	def drone_movement(self):
		print ("---- MOVE : Drone ----")
		
		#i = 0;
		while (self.ennemi_list and (self.out_diameter(int(self.X), int(self.ennemi_list[0].X)) 
			or self.out_diameter(int(self.Y), int(self.ennemi_list[0].Y)) 
			or int(self.Z) != int(self.ennemi_list[0].Z))
			and sqrt((self.ennemi_list[0].X - (g.WIDTH_CANVAS)/2) * (self.ennemi_list[0].X - (g.WIDTH_CANVAS)/2) + (self.ennemi_list[0].Y - (g.HEIGHT_CANVAS)) * (self.ennemi_list[0].Y - (g.HEIGHT_CANVAS))) <= g.VIRTUAL_SCOPE+15) and g.CONTINUE:
			#i += 1;
			#if i == loop_number:
				#i = 0;
			ennemi_event.clear();
			ennemi_event.set();
			time.sleep(t);
			drone_event.wait();

			dY = 2;
			try:
				
				dX = (abs(self.X-self.ennemi_list[0].X) + (abs(self.Y-self.ennemi_list[0].Y)))/(abs(self.Y-self.ennemi_list[0].Y));
				print ("dX/dY = "+str(dX/dY))
				if dX/dY > 8:
					print ("dX too big => replacement : "+str(dX)+" => 1")
					dX = dX/2;
			except:
				# if self.Y == self.ennemi_list[0].Y then calculation is not possible so :
				dX = 1;


			try:
				dZ = abs(self.Z-self.ennemi_list[0].Z)/abs(self.Y-self.ennemi_list[0].Y);
			except:
				dZ = 1;
			

			if self.X > self.ennemi_list[0].X:
				self.X = self.go_left(dX);
				dX = dX * -1; 
			elif self.X < self.ennemi_list[0].X:
				self.X = self.go_right(dX);
			else:
				dX = 0;

			if self.Y > self.ennemi_list[0].Y:
				self.Y = self.go_straight(dY);
				dY = dY * -1;
			elif self.Y < self.ennemi_list[0].Y:
				self.Y = self.go_back(dY);
			else:
				dY = 0;

			if self.Z > self.ennemi_list[0].Z:
				self.Z = self.go_down(dZ);
			elif self.Z < self.ennemi_list[0].Z:
				self.Z = self.go_up(dZ);


			#print("self.X = "+str(self.X)+" dX = "+str(dX))
			self.canvas.move(self.drone, dX, dY);
			self.canvas.move(self.alt_t, dX, dY);
			self.canvas.move(self.name_t, dX, dY);
			self.canvas.itemconfig(self.alt_t, text="Alt : "+str(int(self.Z))+"m");
			self.canvas.update();


			# print ("\nX : "+str(int(self.X))+" "+str(int(self.ennemi_list[0].X)));
			# print ("Y : "+str(int(self.Y))+" "+str(int(self.ennemi_list[0].Y)));
			# print ("Z : "+str(int(self.Z))+" "+str(int(self.ennemi_list[0].Z))+"\n");
			
		# The drone destroyed the ennemi and is destroy too	
		if self.ennemi_list and self.in_diameter(int(self.X), int(self.ennemi_list[0].X)) and self.in_diameter(int(self.Y), int(self.ennemi_list[0].Y)) and int(self.Z) == int(self.ennemi_list[0].Z) and g.CONTINUE:
			self.state = drone_out;
			self.ennemi_list[0].state = drone_out;
			self.label.config(bg="red", text="DRONE "+str(self.id+1)+"\nDestroyed");
		# The ennemi is destroyed but the drone is still OK
		elif self.ennemi_list and g.CONTINUE:
			self.ennemi_list[0].state = drone_ennemi_escaped;

		# Back to GQ if the ennemi escaped or if another drone intersepted it
		if ((self.ennemi_list and self.state == drone_flying and (self.ennemi_list[0].state == drone_ennemi_escaped)) or ((not self.ennemi_list) and self.state == drone_flying)) and g.CONTINUE:
			#print ("In if")
			i = 0;
			self.label.config(text="DRONE "+str(self.id+1)+"\nComing back");
			while (self.out_diameter(self.X, g.WIDTH_CANVAS/2) or self.Y < g.HEIGHT_CANVAS or int(self.Z) != 1) and g.CONTINUE:
				
				#print ("In while")
				i += 1;
				if i == loop_number and self.ennemi_list:
					i = 0;
					ennemi_event.clear();
					ennemi_event.set();
					time.sleep(t);
					drone_event.wait();
				try:
					dX = abs(self.X-g.WIDTH_CANVAS/2)/abs(self.Y-g.HEIGHT_CANVAS);
				except:
					dX = 1;
				dY = 1;
				if int(self.X) > g.WIDTH_CANVAS/2:
					self.X = self.go_left(dX);
					dX = dX * -1;
				elif int(self.X) < g.WIDTH_CANVAS/2:
					self.X = self.go_right(dX);
				else:
					dX = 0;

				if int(self.Y) > g.HEIGHT_CANVAS:
					self.Y = self.go_straight(dY);
					dY = dY * -1;
				elif int(self.Y) < g.HEIGHT_CANVAS:
					self.Y = self.go_back(dY);
				else:
					dY = 0;

				if self.Z >= 2:
					dZ = 1
					self.Z = self.go_down(dZ);

				#print ("\nX : "+str(int(self.X)));
				#print ("Y : "+str(int(self.Y)));
				#print ("Z : "+str(int(self.Z))+"\n");
				#print (self.X - g.WIDTH_CANVAS/2)
				#print (self.Y)
				#print (g.HEIGHT_CANVAS)
				#print (self.Y - g.HEIGHT_CANVAS)
				self.canvas.move(self.drone, dX, dY);
				self.canvas.move(self.alt_t, dX, dY);
				self.canvas.move(self.name_t, dX, dY);
				self.canvas.itemconfig(self.alt_t, text="Alt : "+str(int(self.Z))+"m");
				self.canvas.update();

			print ("Back home");
			self.state = drone_back;	# Drone back of a mission ready for inspection
			self.label.config(bg="blue", text="DRONE "+str(self.id+1)+"\nBack");
			# if the ennemi escaped we get him out of the list
			if self.ennemi_list:
				self.ennemi_list[0].state = drone_out;

		print("---- END ALLY MOVE ----");

	def run(self):

		if self.kind == "ennemi":
			self.ennemi_movement();
		elif self.kind == "ally":
			self.drone_movement();
			




