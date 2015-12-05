from graphics import Window
import graphics as g
from radar import Radar
from drone import Drone
import time



thread_list = [];
current_thread = 0;

if __name__ == '__main__':
	
	# Possible state of a drone
	drone_out          = 0;	# Drone on his spot but damage so a fly is impossible 
	drone_backprogress = 1;	# Drone is coming back of his mission
	drone_ready        = 2;	# Drone on his spot and operational
	drone_flying       = 3;	# Drone in mission flying through the target
	drone_back         = 4;	# Drone back of a mission ready for inspection
	drone_destroyed    = 5;	# Drone destroyed during a mission
	drone_detected     = 6;	# Drone ennemi dedetected
	
	p = 30
	Win = Window(thread_list);
	
	radar = Radar(thread_list, Win.get_canvas(), Win.get_label_list(), Win.get_intruder_b(), Win.get_repare_b());
	thread_list.append(radar);
	print ("---- Drones 1 to "+str(g.NUMBER_DRONE)+" initialization ----");
	for i in range(g.NUMBER_DRONE):
		print ("Drone : "+ str(i+1));
		X = ((Win.get_width_zone() - g.NUMBER_DRONE * p) / 2 + p * i + p/2) * g.DIMENSION_COEFFICIENT;
		Y = Win.get_origine_Y() - 20 * g.DIMENSION_COEFFICIENT;
		Z = 0;
		drone = Drone(Win.get_canvas(), i, X, Y, Z, thread_list, Win.get_label_list()[i], 0, -1);
		thread_list.append(drone);
		print ("id = "+str(thread_list[i+1].id)+" "+str(thread_list[i+1].kind))


	radar.start();
	
	Win.get_window().mainloop();