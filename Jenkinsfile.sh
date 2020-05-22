set -e

WORKSPACE_ROOT="$WORKSPACE/$BUILD_NUMBER"
TEST_OUTPUT_DIR="$WORKSPACE_ROOT/test-output"
TEST_DATA_DIR="$WORKSPACE/../../../test-data"
mkdir $TEST_OUTPUT_DIR

#Custom home for this run's temporary stuff
rm -rf ~/.stimela
HOME=$WORKSPACE_ROOT
export HOME
SINGULARITY_STORAGE="${WORKSPACE}/../../../.singularity"
ln -s $WORKSPACE/../../../.udocker ${WORKSPACE_ROOT}/.udocker
ln -s ${SINGULARITY_STORAGE} ${WORKSPACE_ROOT}/.singularity

# setup podman image storage. Using .singularity volume
POD_STORAGE="${WORKSPACE_ROOT}/.local/share/containers/storage"
mkdir -p ${POD_STORAGE} ${SINGULARITY_STORAGE}/podman
ln -s ${SINGULARITY_STORAGE}/podman ${POD_STORAGE}

# Copy a clean dataset over
mkdir $TEST_OUTPUT_DIR/msdir
tar -xzvf $TEST_DATA_DIR/kat-7-small.ms.tar.gz -C $TEST_OUTPUT_DIR/msdir
tar -xvf $TEST_DATA_DIR/DEEP2.ms.tar.gz -C $TEST_OUTPUT_DIR/msdir
mkdir $TEST_OUTPUT_DIR/input
cp -r $TEST_DATA_DIR/beams $TEST_OUTPUT_DIR/input/beams

docker -v
podman -v
singularity -v
export STIMELA_PULLFOLDER=${WORKSPACE_ROOT}/singularity_images
mkdir $STIMELA_PULLFOLDER

#########################################################################
# PYTHON 3 TEST
#########################################################################
rm -rf ~/.stimela
OLDPATH=$PATH
OLDLDPATH=$LD_LIBRARY_PATH

# Install Stimela into a virtual env
virtualenv -p python3 ${WORKSPACE_ROOT}/projects/pyenv
. ${WORKSPACE_ROOT}/projects/pyenv/bin/activate
#pip install pip setuptools -U
PATH=${WORKSPACE}/projects/pyenv/bin:$PATH
LD_LIBRARY_PATH=${WORKSPACE}/projects/pyenv/lib:$LD_LIBRARY_PATH
pip install ${WORKSPACE_ROOT}/projects/Stimela/

stimela --version
stimela pull --force

#Run forest run!
cd $TEST_OUTPUT_DIR
export SILENT_STDERR=ON
python3 -m nose --with-xunit --xunit-file $WORKSPACE_ROOT/nosetests.xml "${WORKSPACE_ROOT}/projects/Stimela/stimela/tests"

