from graphics import Application
from radar import Radar
from drone import Drone

if __name__ == '__main__':

	REAL_SCOPE         = 350;
	VIRTUAL_SCOPE      = 0;
	# Height equivalency (in meters)
	HEIGHT_SCALE       = 400;
	NUMBER_ALLY_DRONE  = 1;
	
	# Possible state of a drone
	drone_out          = 0;	# Drone on his spot but damage so a fly is impossible 
	drone_backprogress = 1;	# Drone is coming back of his mission
	drone_ready        = 2;	# Drone on his spot and operational
	drone_flying       = 3;	# Drone in mission flying through the target
	drone_back         = 4;	# Drone back of a mission ready for inspection
	drone_destroyed    = 5;	# Drone destroyed during a mission
	drone_detected     = 6;	# Drone ennemi dedetected
	
	drone_list = [];

	App = Application();
	
	
	
	print ("---- Drones 1 to 6 initialization ----");
	for i in range(6):
		print ("Drone : "+ str(i+1));
		X = App.get_width_canvas()/2;
		Y = App.get_height_canvas()+10;
		Z = 0;
		drone = Drone("ally", i, App.get_CANVAS_C(), X, Y, Z, App.get_ennemi_list(), App.get_label_list()[i]);
		drone_list.append(drone);


	Radar = Radar(drone_list, App.get_ennemi_list(), App.get_CANVAS_C(), App.get_label_list());
	Radar.start();

	App.win.mainloop();