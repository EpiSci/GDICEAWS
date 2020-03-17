import math
import random
from adt import Configuration
def setval(minimum, maximum):
    return random.uniform(minimum, maximum)
def newconfig(idxRun):
	config = Configuration()

	# Lateral Separation
	config.set(RED_INITIAL_LAT=setval(21.3, 21.31375))
	config.set(BLUE_INITIAL_LAT=setval(21.3, 21.31375))

	# Forward Separation
	config.set(RED_INITIAL_LONG=setval(-157.8, -157.81467))
	config.set(BLUE_INITIAL_LONG=setval(-157.8, -157.81467))

	# Red Aircraft Altitude
	config.set(RED_INITIAL_ALTITUDE_FT=setval(2000, 20000))

	# Blue Aircraft Altitude
	config.set(BLUE_INITIAL_ALTITUDE_FT=setval(2000, 20000))

	# Relative Heading
	config.set(RED_INITIAL_HEADING_DEG=setval(0, 360))
	config.set(BLUE_INITIAL_HEADING_DEG=setval(0, 360))

	# Red Aircraft Speed
	config.set(RED_INITIAL_U=setval(338, 1012))

	# Blue Aircraft Speed
	config.set(BLUE_INITIAL_U=setval(338, 1012))

	# Red Aircraft Fuel Load
	config.set(RED_INITIAL_MIXTURE_CMD=setval(0.4, 1.0))

	# Blue Aircraft Fuel Load
	config.set(BLUE_INITIAL_MIXTURE_CMD=setval(0.4, 1.0))

	# Hard Deck
	config.set(BOUNDARY_ALT_FLOOR=1000)

	config.write_configuration("configuration/rc"+ str(idxRun) +".xml")
