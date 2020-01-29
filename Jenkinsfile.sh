set -e

WORKSPACE_ROOT="$WORKSPACE/$BUILD_NUMBER"
TEST_OUTPUT_DIR="$WORKSPACE_ROOT/test-output"
TEST_DATA_DIR="$WORKSPACE/../../../test-data"
mkdir $TEST_OUTPUT_DIR

#Custom home for this run's temporary stuff
HOME=$WORKSPACE_ROOT
export HOME
SINGULARITY_STORAGE="${WORKSPACE}/../../../.singularity"
ln -s $WORKSPACE/../../../.udocker ${WORKSPACE_ROOT}/.udocker
ln -s ${SINGULARITY_STORAGE} ${WORKSPACE_ROOT}/.singularity

# setup podman image storage. Using .singularity volume
POD_STORAGE="${WORKSPACE_ROOT}/.local/share/containers/storage"
mkdir -p ${POD_STORAGE} ${SINGULARITY_STORAGE}/podman
ln -s ${SINGULARITY_STORAGE}/podman ${POD_STORAGE}


# Install Stimela into a virtual env
virtualenv ${WORKSPACE_ROOT}/projects/pyenv -p python3
. ${WORKSPACE_ROOT}/projects/pyenv/bin/activate
pip install pip setuptools -U
OLDPATH=$PATH
OLDLDPATH=$LD_LIBRARY_PATH
PATH=${WORKSPACE}/projects/pyenv/bin:$PATH
LD_LIBRARY_PATH=${WORKSPACE}/projects/pyenv/lib:$LD_LIBRARY_PATH
python3 -m pip install ${WORKSPACE_ROOT}/projects/Stimela/

# Copy a clean dataset over
mkdir $TEST_OUTPUT_DIR/msdir
tar -xzvf $TEST_DATA_DIR/kat-7-small.ms.tar.gz -C $TEST_OUTPUT_DIR/msdir
mkdir $TEST_OUTPUT_DIR/input
cp -r $TEST_DATA_DIR/beams $TEST_OUTPUT_DIR/input/beams

stimela --version
singularity -v
docker -v
export SINGULARITY_PULLFOLDER=${WORKSPACE_ROOT}/singularity_images
mkdir $SINGULARITY_PULLFOLDER
stimela pull -s -cb simms
#stimela pull -cb tricolour
#stimela pull -p -cb casa_listobs
# fresh build
stimela build -nc

#Run forest run!
cd $TEST_OUTPUT_DIR
nosetests --with-xunit --xunit-file $WORKSPACE_ROOT/nosetests.xml "${WORKSPACE_ROOT}/projects/Stimela/stimela/tests"

#Run 2.7 tests
virtualenv ${WORKSPACE_ROOT}/projects/pyenv27 -p python2.7
. ${WORKSPACE_ROOT}/projects/pyenv27/bin/activate
pip install pip setuptools -U
PATH=$OLDPATH
LD_LIBRARY_PATH=$OLDLDPATH
PATH=${WORKSPACE}/projects/pyenv/bin:$PATH
LD_LIBRARY_PATH=${WORKSPACE}/projects/pyenv27/lib:$LD_LIBRARY_PATH
python2.7 -m pip install ${WORKSPACE_ROOT}/projects/Stimela/

cd $TEST_OUTPUT_DIR
nosetests --with-xunit --xunit-file $WORKSPACE_ROOT/nosetests.xml "${WORKSPACE_ROOT}/projects/Stimela/stimela/tests/unit_tests"

rm -rf $SINGULARITY_PULLFOLDER/* # delete the compiled images after testing is done
