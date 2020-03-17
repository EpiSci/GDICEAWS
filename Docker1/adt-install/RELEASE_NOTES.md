# Release Notes

## Changelog

### v1.3.2 - 11/11/2019
* [ACE-235] Consistent scoring positions to half angles and renamed scoring angle parameters
* [ACE-237] Moved Bud FSM to adt/agents folder and updated requirements for installer
* [ACE-239] Fix version strings
* [ACE-240] Update Bud logic for new scoring configuration

### v1.3.1 - 11/8/2019
* [ACE-232] Make tracking condition defense based off of the velocity vector
* [ACE-231] Add acceleration clipping of the elevator
* [ACE-234] Make fuel state configurable
* [ACE-227] Track and Tracking Flags no resetting
* [ACE-226] Bud is unstable when starting back-to-back
* [ACE-223] Configurable Parameters for Scoring
* [ACE-224] Reactive Boundary Doesn't Match Simulation
* [ACE-216] Fix PID Agent reset functions to reset all errors in controller

### v1.3.0 - 11/1/2019
* [ACE-81]  Shading makes it hard to distinguish red from blue in adt-viewer
* [ACE-119] High security vulnerability warning during installation
* [ACE-147] Get xgrip working with joy
* [ACE-178] Range ring in dis visualizer doesn't change with config
* [ACE-205] Autodoc error on install.
* [ACE-207] Track angle dict key implies radians
* [ACE-211] Allow change initial conditions on reset
* [ACE-212] Add DIS ID terms to the list of configurables
* [ACE-215] Add Tracking/Tracked Progress States

### v1.2.0 - 10/18/2019
* Changed default values in configuration and added options (see configuration.py or print configuration object)
* [ACE-202] Track Angle fixed to account for pitch rotation
* [ACE-195] Added net thrust force to statespace for ownship
* [ACE-161] Left / right aileron values replaced by single normalized aileron position value
* [ACE-175] reset method in Manager now resets done flag properly
* [ACE-159] Beta statespace variable now is correctly given
* [ACE-171] Now both engines for F-15 changed by throttle command
* [ACE-165] log_state fix checks if DEBUG before writing debug logging statements
* [ACE-110] Change implementation of FlightGear to Multiplayer
* [ACE-203] Matplot now plots action space for both red and blue aircraft
* [ACE-164] Added configurable parameter to disable sim time output to console
* [ACE-184] Altitude floor boundary is now a configurable parameter and default of 200 ft
* [ACE-193] Added action space and observation space box to agent
* [ACE-129] First state values now reported correctly after environment reset
* [ACE-160] Track angle bounds now reported in degrees like their value
* [ACE-172] Environment reset returns an info dictionary of state variables names
* [ACE-149] Renamed 'adt-framework-information' to 'adt-sim-env-info'
* [ACE-204] REAL_TIME_MULTIPLE can be any float greater than 0
* [ACE-180] Updated default sim frequency definitions in code constructors
* [ACE-201] Remove last reward and last assessed reward from plot vis 

### v1.1.0 - 10/4/2019
* Added release notes.
* Fixed issue where the blue state being returned from gym_jsbsim contains the red state in the tuple.
* Corrected README.md to have correct name of package installer.
* Corrected README.md to emphasize not running install script as sudo.
* [ACE-1] Corrected segmentation fault when jsbsim exits.
* [ACE-80] Corrected issue where PID agents crash after calling manager.reset() a second time.
* [ACE-95] Added list of network ports to HTML documentation.
* [ACE-96] Removed compete_local_agent_vs_adt_agent.py from example code.
* [ACE-99] Installer no longer allows running as root.
* [ACE-100] Fixed divide by zero error in controllers
* [ACE-101] Made the DIS packet destination from gym-jsbsim configurable.
* [ACE-104] Added information to README.md for working with SSL Proxies.
* [ACE-108] Clipped action space input to prevent throttle >2.
* [ACE-114] Corrected adt-viewer socket address to permit accessing adt-viewer from a web browser on another machine.
* [ACE-115] stop-adt-viewer no longer kills node process that are not part of adt-viewer.
* [ACE-117] Added caveats to README.md for shells other than bash.
* [ACE-118] Removed pkg-resources from requirements.txt.
* [ACE-123] Ensured Gym Space Box allows the throttle to go to 2.
* [ACE-126] Re-implement don't-wait-on-agent feature.
* [ACE-130] is_done boolean is now forwarded to agent.
* [ACE-132] The final reward is now passed to the agent.
* [ACE-135] adt Python package installed with pip for consistency.
* [ACE-139] Sideslip and angle of attack added to state space.
* [ACE-140] Extraneous blank lines removed from beginning of example code.
* [ACE-142] Make reward responsive to new frequency.
* [ACE-143] Added an index:state name dictionary in the info for all items in the state space.
* [ACE-144] Fixed highs and lows in statespace bounds.
* [ACE-150] Added a reset method to agents.
* [ACE-152] Added agent update time constraint.
* [ACE-153] Broke the Interface class into AgentInterface, AgentBase, and AgentActionComputeThread.

### v1.0.0 - 9/30/2019
* Initial release.

## Known Issues
* [ACE-168] Prior fail in apt-get blocks npm install
* [ACE-236] Home button on Cesium viewer not working properly


