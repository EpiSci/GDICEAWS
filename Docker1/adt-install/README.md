# ADT Simulation Environment

## Overview
This installer package installs all required prerequisites and the ADT simulation environment itself onto a freshly installed Ubuntu 18.04 Desktop machine. Required Debian packages will be installed directly to the system, but all the Python modules will be installed to a dedicated virtual environment to isolate the simulation environment from system Python. Following the installation, all new terminals will automatically activate the virtual environment, allowing all Python modules from the ADT Simulation Environment to be available to performer autonomy implementations.

This package installs a basic TensorFlow without GPU support. If GPU support is desired, the user should unintall the existing TensorFlow installation and reinstall the appropriate package, ensuring all actions take place within the Python virtual environment.

## Prerequisites
This installer assumes you are running a fresh "Normal" Ubuntu 18.04 with a user account can run commands as root using sudo.

This installation process also requires Internet access.

## Installation
1) Log on to the Ubuntu 18.04 computer as a user that is an Administrator.
2) Copy the `install-adt.tar.gz` to the user's home directory.
3) From the user's home directory, run `tar xvzf adt-install-v<x.x.x>.tar.gz` to unpack the installation file.
4) Change directory to `adt-install`.
5) Install the ADT Simluation Environment by typing `./install-adt.sh`. DO NOT RUN THIS COMMAND WITH SUDO. You will be required to type your password for certain sudo commands to execute. At some point you will need to accept or reject sending analytic information. This package does NOT require sending analytic information.
6) Close and open a new terminal window or source ~/.bashrc to pick up changes inserted by the installer.

NOTE: By default the installer will add a line to your .bashrc to activation of the Python virtual environment automatically for future terminals. If this behavior is not desired, add the `-n` flag when running the installer. If you use `-n` you will be responsible for activating the virtual environment yourself. (See `Using the environment`)

## Using the environment
Once the installer is completed, the jsbsim and gym-jsbsim modules will all be available for import whenever the ADT virtual environment is active. By default, the environment will activate for every new terminal once the installer completes. To manually activate the virtual environment, type `. ~/.adt/venv-adt/bin/activate`.

When the virtual environment is running, you will see `(venv-adt)` at the beginning of all prompts.

To deactivate the virtual environment, type `deactivate`.

The installer creates a directory called `adt-sim-env-info` in the user's home directory with HTML documentation and sample code.

## Using the adt-viewer
The ADT Viewer allows the user to visualize the simulated aircraft in a global world display. The installer puts aliases in .bashrc for easy start/stop of the adt-viewer.
- To start the adt-viewer, type `start-adt-viewer`.
- To stop the adt-viewer, type `stop-adt-viewer`.
- Go to localhost:8080 in browser of choice. (Developed on latest Firefox)

## Using the FlightGear visualizer
The FlightGear visualizer allows the user to visualize the simulated aircraft in a cockpit view. FlightGear utilizes UDP ports for comms between the simulation and the visualization and between multiplayer instances of the visualization.
- Edit your config.xml file with the correct SERVER value. This should be the IP address of the computer you are using. Do not use 'localhost' if you are planning on running a mulitplayer instance.
- If you are using any of the default UDP ports, you may change those as well.
- In order for multiplayer to work, you must set both FG_RED and FG_BLUE to True.

## Special Notes

### Alternate Shells
This installer assumes the bash shell, and installs features to .bashrc to ease the user experience. If you choose to use a different shell, you will need to manually perform the following, or use your shell's method to make these persist:
* Activate the Python virtual environment with `. ~/.adt/venv-adt/bin/activate`.
* Alias start-adt-viewer to: `/bin/bash ~/.adt/dis-viewer/start-adt-viewer.sh`.
* Alias stop-adt-viewer to: `/bin/bash ~/.adt/dis-viewer/stop-adt-viewer.sh`.

### Working around SSL Proxies
Organizations that use SSL proxies will need to put measure in place to allow
apt-get, git, npm, and node to use their internal root certificate. The methods to do
this may vary from organization to organization. Here are some possible approaches:
* apt-get: Install your root certificate to the Ubuntu operating system by copying 
the certificate to /usr/local/share/ca-certificates with a .crt extention, then running `sudo update-ca-certificates`.
* pip: After installing the root certificate to the system, tell pip to use this certificate by exporting the following environment variable. This can be added to ~.bashrc: `export PIP_CERT=/etc/ssl/certs/ca-certificates.crt`
* npm: After installing the root certificate to the system, add the following to ~/.npmrc, creating the file if necessary: `cafile=/etc/ssl/certs/ca-certificates.crt`.
* node: After installing the root certificate to the system, tell node to use this certificate by exporting the following environment variable. This can be added to ~.bashrc: `export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt`.
