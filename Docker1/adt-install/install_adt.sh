#!/bin/bash

INSTALL_DIR=${PWD}
TARGET_DIR=~/.adt
OLD_SAMPLE_DIR=~/adt-framework-information
SAMPLE_DIR=~/adt-sim-env-info

BUNDLES=true
BASHRC=true
CLEAN=false

REQUIRED_REPOS="jsbsim gym-jsbsim dis-viewer adt-autonomy"

check_bundles() {
  OK=true
  cd ${INSTALL_DIR}/deps
  for repo in $REQUIRED_REPOS; do
    if [ ! -e ${repo}.bundle ]; then
      echo "Missing required bundle ${repo}.bundle. Use -r if you have cloned the repos."
      OK=false
    fi
  done

  !($OK) && exit 1
}

check_repos() {
  OK=true
  cd ${INSTALL_DIR}/deps
  for repo in $REQUIRED_REPOS; do
    if [ ! -e ${repo} ]; then
      echo "Missing required repo ${repo}. Get rid of the -r if you are using bundles."
      OK=false
    fi
  done

  !($OK) && exit 1
}


expand_bundles() {
  cd ${INSTALL_DIR}/deps
  for repo in $REQUIRED_REPOS; do
      [ -e $repo ] && rm -rf $repo
      git clone -b master ${repo}.bundle
  done
}

usage() {
      echo "Usage: ./install_adt_idi.sh [-r] [-n]"
      echo ""
      echo "    -r: Do not clone git bundles. Assume repos are already cloned into ./deps."
      echo "    -n: Do not alter .bashrc to automatically activate the venv when starting a new terminal."
      echo "    -c: Perform a cleaner than normal installation. Do not use unless directed by support."
      echo ""
      exit 0
}

while getopts ":hrnc" opt; do
  case ${opt} in
    r )
      BUNDLES=false
      ;;
    n )
      BASHRC=false
      ;;
    c )
      CLEAN=true
      ;;
    h )
      usage
      ;;
    \? )
      usage
      ;;
  esac
done

if $BUNDLES; then #check for required bundles
  check_bundles
else
  check_repos
fi

#Install Ubuntu packages
apt update
echo "*** Installing Ubuntu packages ***"
 systemctl stop packagekit
yes '' |  add-apt-repository ppa:saiarcot895/flightgear
 apt-get update
 apt-get install -y git python3 python3-pip python3-venv python3-tk python3-dev cython cmake flightgear curl tmux libopenmpi-dev zlib1g-dev joystick mariadb-server graphviz-dev

# Install node/npm/Angular
echo "*** Installing node, npm, Angular, and http-server"
curl -sL https://deb.nodesource.com/setup_10.x |  bash - # Would like to find something more secure
 apt-get install -y nodejs
 npm install -g @angular/cli http-server
 chown -R ${USER}:${USER} ~/.npm

 systemctl start packagekit

# Get F-15 model
if [ ! -e /usr/share/games/flightgear/Aircraft/F-15 ]; then
    echo "*** Downloading F-15 model ***"
    wget http://mirrors.ibiblio.org/flightgear/ftp/Aircraft/F-15.zip
     mv F-15.zip /usr/share/games/flightgear/Aircraft
    cd /usr/share/games/flightgear/Aircraft
     unzip F-15.zip
     rm F-15.zip
fi

if $BUNDLES; then # clone bundles
  expand_bundles
fi

if $CLEAN; then
    echo "*** -c used, so removing target directory ${TARGET_DIR} ***"
    [ -e ${TARGET_DIR} ] && rm -rf ${TARGET_DIR}
fi

echo "*** Creating target directory ${TARGET_DIR} ***"
mkdir -p ${TARGET_DIR}

# Make virtual environment
echo "*** Creating Python 3 virtual environment if necessary ***"
cd ${TARGET_DIR}
[ ! -e venv-adt ] && python3 -m venv venv-adt

if $BASHRC; then
    echo "*** Adding Python virtual environment activation to ~/.bashrc"
    grep -qxF ". ${TARGET_DIR}/venv-adt/bin/activate" ~/.bashrc || echo ". ${TARGET_DIR}/venv-adt/bin/activate" >> ~/.bashrc
fi

# Switch to the virtual environment
. ${TARGET_DIR}/venv-adt/bin/activate

echo "*** Installing PyPI Python packages ***"
# Upgrade pip, setuptools
pip install --upgrade pip setuptools

# Install Python packages from PyPI
cd ${INSTALL_DIR}
pip install -r requirements.txt

# Install gym-jbsim and Open-DIS utilities
echo "*** Installing gym-jsbsim *** "
cd ${INSTALL_DIR}/deps/gym-jsbsim
pip install .

echo "*** Installing Open-DIS utilities ***"
cd ${INSTALL_DIR}/deps/gym-jsbsim/gym_jsbsim/dis
pip install .

# Install ADT
echo "*** Installing ADT"
cd ${INSTALL_DIR}/deps/adt-autonomy
pip install .

# Install jsbsim
echo "*** Installing jsbsim ***"
cd  ${INSTALL_DIR}/deps/jsbsim
rm -Rf build
mkdir build
cd build
cmake ..
make
 make install
python python/setup.py install --skip-build
[ -e ${TARGET_DIR}/jsbsim ] && rm -rf ${TARGET_DIR}/jsbsim
cd ${INSTALL_DIR}/deps
cp -pr jsbsim ${TARGET_DIR}/

# Copy documentation and sample code
cd ${INSTALL_DIR}/deps/adt-autonomy/docs
make html
rm -rf ${INSTALL_DIR}/deps/adt-autonomy/exposed_to_performer/docs
cp -r ${INSTALL_DIR}/deps/adt-autonomy/docs/build/html/ ${INSTALL_DIR}/deps/adt-autonomy/exposed_to_performer/docs
cd ${INSTALL_DIR}/deps/adt-autonomy/exposed_to_performer
[ -e ${OLD_SAMPLE_DIR} ] && rm -rf ${OLD_SAMPLE_DIR}
[ -e ${SAMPLE_DIR} ] && rm -rf ${SAMPLE_DIR}
mkdir -p ${SAMPLE_DIR}
cp -pr * ${SAMPLE_DIR}

# Install dis-viewer
echo "*** Installing adt-viewer ***"
[ -e  ${TARGET_DIR}/dis-viewer ] && rm -rf  ${TARGET_DIR}/dis-viewer
cd  ${INSTALL_DIR}/deps
cp -pr dis-viewer ${TARGET_DIR}/
cd ${TARGET_DIR}/dis-viewer/Dis-Serve
npm install
cd ${TARGET_DIR}/dis-viewer/ACEV
npm install
ng build
grep -qxF "alias start-adt-viewer='/bin/bash ${TARGET_DIR}/dis-viewer/start-adt-viewer.sh'" ${HOME}/.bashrc || echo "alias start-adt-viewer='/bin/bash ${TARGET_DIR}/dis-viewer/start-adt-viewer.sh'" >> ${HOME}/.bashrc
grep -qxF "alias stop-adt-viewer='/bin/bash ${TARGET_DIR}/dis-viewer/stop-adt-viewer.sh'" ${HOME}/.bashrc || echo "alias stop-adt-viewer='/bin/bash ${TARGET_DIR}/dis-viewer/stop-adt-viewer.sh'" >> ${HOME}/.bashrc
grep -qxF "plugin_load_add = ha_blackhole" ${HOME}/.my.cnf || printf "[mariadb]\nplugin_load_add = ha_blackhole\n" >> ${HOME}/.my.cnf
