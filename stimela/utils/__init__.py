import subprocess
import signal
import os
import sys
import logging
import json
import codecs
import time
import tempfile
import inspect
import warnings
import re

from multiprocessing import Process, Manager, Lock
manager = Manager()

CPUS = 1

def logger(level=0, logfile=None):

    if logfile:
        logging.basicConfig(filename=logfile)
    else:
        logging.basicConfig()

    LOGL = {"0": "INFO",
            "1": "DEBUG",
            "2": "ERROR",
            "3": "CRITICAL"}

    log = logging.getLogger("STIMELA")
    log.setLevel(eval("logging."+LOGL[str(level)]))

    return log


def assign(key, value):
    frame = inspect.currentframe().f_back
    frame.f_globals[key] = value


def xrun(command, options, log=None, _log_container_as_started=False, logfile=None):
    """
        Run something on command line.

        Example: _run("ls", ["-lrt", "../"])
    """

    cmd = " ".join([command]+ map(str, options) )

    if log:
        log.info("Running: %s"%cmd)
    else:
        print('running: %s'%cmd)

    process = subprocess.Popen(cmd,
                  stderr=subprocess.PIPE if not isinstance(sys.stderr,file) else sys.stderr,
                  stdout=subprocess.PIPE if not isinstance(sys.stdout,file) else sys.stdout,
                  shell=True)

    if process.stdout or process.stderr:

        out, err = process.comunicate()
        sys.stdout.write(out)
        sys.stderr.write(err)
        return out
    else:
        process.wait()
    if process.returncode:
         raise SystemError('%s: returns errr code %d'%(command, process.returncode))


def pper(iterable, command, cpus=None, stagger=2, logger=None):
    """
       Run command in parallel.
       
       iterable :  argument(s) to iterate over
       command : callable command to run
       cpus : number of cpus to use
       stagger : stagger jobs (in seconds)
       logger : logging instance
    """

    cpus = cpus or CPUS

    if not hasattr(iterable, "__iter__"):
        raise TypeError("Can not iterate over [%s]. Make its iterable"%iterable)

    if not callable(command):
        raise TypeError("command [%] is not callable"%(command.func_name))

    message = "Iterating over :: %s"%repr(iterable)

    if logger:
        logger.info(message)
    else:
        print message


    active = manager.Value("d", 0)
    
    def worker(*args):
        command(*args)
        active.value -= 1

    nprocs = len(iterable)
    counter = 0
    procs = []

    while counter <= nprocs-1:
        if active.value >= cpus:
            continue
        
        time.sleep(stagger)
        active.value += 1
        args = iterable[counter]

        if not hasattr(args, "__iter__"):
            args = (args,)

        proc = Process(target=worker, args=args)
        procs.append(proc)
        proc.start()
        counter += 1


    for proc in procs:
        proc.join()



def readJson(conf):
   import collections

   with open(conf) as _std:
       jdict = json.load(_std)

   ndict = {}
   for key,val in jdict.items():
        if isinstance(val, unicode):
            val = str(val)

        elif isinstance(val, (list,tuple)):
            for i,v in enumerate(val):
                if isinstance(v, unicode):
                    val[i] = str(v)
       
        ndict[str(key)] = val
   return ndict


def writeJson(config, dictionary):
    with codecs.open(config, 'w', 'utf8') as std:
        std.write(json.dumps(dictionary, ensure_ascii=False))


def get_Dockerfile_base_image(image):

    if os.path.isfile(image):
        dockerfile = image
    else:
        dockerfile = "{:s}/Dockerfile".format(image)

    with open(dockerfile, "r") as std:
        _from = "" 
        for line in std.readlines():
            if line.startswith("FROM"):
                _from = line
        
    return _from


def change_Dockerfile_base_image(path, _from, label, destdir="."):
    if os.path.isfile(path):
        dockerfile = path
        dirname = os.path.dirname(path)
    else:
        dockerfile = "{:s}/Dockerfile".format(path)
        dirname = path

    with open(dockerfile, "r") as std:
        lines = std.readlines()
        for line in lines:
            if line.startswith("FROM"):
                lines.remove(line)

    temp_dir = tempfile.mkdtemp(prefix="tmp-stimela-{:s}-".format(label), dir=destdir)
    xrun("cp", ["-r", "{:s}/Dockerfile {:s}/src".format(dirname, dirname), temp_dir])

    dockerfile = "{:s}/Dockerfile".format(temp_dir)

    with open(dockerfile, "w") as std:
        std.write("{:s}\n".format(_from))

        for line in lines:
            std.write(line)

    return temp_dir, dockerfile


def get_base_images(logfile, index=1):
    
    with open(logfile) as std:
        string = std.read()

    separator = "[================================DONE==========================]"

    log = string.split(separator)[index-1]

    images = []

    for line in log.split("\n"):
        if line.find("<=BASE_IMAGE=>")>0:
            tmp = line.split("<=BASE_IMAGE=>")[-1]
            image, base = tmp.split("=")
            images.append((image.strip(), base))
    
    return images


def icasa(taskname, mult=None, loadthese=[],**kw0):
    """ 
      runs a CASA task given a list of options.
      A given task can be run multiple times with a different options, 
      in this case the options must be parsed as a list/tuple of dictionaries via mult, e.g 
      icasa('exportfits',mult=[{'imagename':'img1.image','fitsimage':'image1.fits},{'imagename':'img2.image','fitsimage':'image2.fits}]). 
      Options you want be common between the multiple commands should be specified as key word args.
    """

    # create temp directory from which to run casapy
    td = tempfile.mkdtemp(dir='.')
    # we want get back to the working directory once casapy is launched
    cdir = os.path.realpath('.')

    # load modules in loadthese
    _load = ""
    if "os" not in loadthese or "import os" not in loadthese:
        loadthese.append("os")

    if loadthese:
        exclude = filter(lambda line: line.startswith("import") or line.startswith("from"), loadthese)
        for line in loadthese:
            if line not in exclude:
                line = "import %s"%line
            _load += "%s\n"%line

    if mult:
        if isinstance(mult,(tuple,list)):
            for opts in mult:
                opts.update(kw0)
        else:
            mult.upadte(kw0)
            mult = [mult]
    else:
        mult = [kw0]

    run_cmd = """ """
    for kw in mult:
        task_cmds = ''
        for key,val in kw.iteritems():
            if isinstance(val,(str, unicode)):
                 val = '"%s"'%val
            task_cmds += '\n%s=%s'%(key,val)
        run_cmd += """ 
%s

os.chdir('%s')
taskname = '%s'
%s
go()

"""%(_load,cdir, taskname, task_cmds)

    tf = tempfile.NamedTemporaryFile(suffix='.py')
    tf.write(run_cmd)
    tf.flush()
    t0 = time.time()
    # all logging information will be in the pyxis log files 
    xrun("cd", [td, "&& casa --nologger --log2term --nologfile -c", tf.name])

    # log taskname.last 
    task_last = '%s.last'%taskname
    if os.path.exists(task_last):
        with open(task_last,'r') as last:
            print('%s.last is: \n %s'%(taskname, last.read()))

    # remove temp directory. This also gets rid of the casa log files; so long suckers!
    xrun("rm", ["-fr ", td, task_last])
    tf.close()


def stack_fits(fitslist, outname, axis=0, ctype=None, keep_old=False, fits=False):
    """ Stack a list of fits files along a given axiis.
       
       fitslist: list of fits file to combine
       outname: output file name
       axis: axis along which to combine the files
       fits: If True will axis FITS ordering axes
       ctype: Axis label in the fits header (if given, axis will be ignored)
       keep_old: Keep component files after combining?
    """
    import numpy
    try:
        import pyfits
    except ImportError:
        warnings.warn("Could not find pyfits on this system. FITS files will not be stacked")
        sys.exit(0)

    hdu = pyfits.open(fitslist[0])[0]
    hdr = hdu.header
    naxis = hdr['NAXIS']

    # find axis via CTYPE key
    if ctype is not None:
        for i in range(1,naxis+1):
            if hdr['CTYPE%d'%i].lower().startswith(ctype.lower()):
                axis = naxis - i # fits to numpy convention
    elif fits:
      axis = naxis - axis

    fits_ind = abs(axis-naxis)
    crval = hdr['CRVAL%d'%fits_ind]

    imslice = [slice(None)]*naxis
    _sorted = sorted([pyfits.open(fits) for fits in fitslist],
                    key=lambda a: a[0].header['CRVAL%d'%(naxis-axis)])

    # define structure of new FITS file
    nn = [ hd[0].header['NAXIS%d'%(naxis-axis)] for hd in _sorted]
    shape = list(hdu.data.shape)
    shape[axis] = sum(nn)
    data = numpy.zeros(shape,dtype=float)

    for i, hdu0 in enumerate(_sorted):
        h = hdu0[0].header
        d = hdu0[0].data
        imslice[axis] = range(sum(nn[:i]),sum(nn[:i+1]) )
        data[imslice] = d 
        if crval > h['CRVAL%d'%fits_ind]:
            crval =  h['CRVAL%d'%fits_ind]

    # update header
    hdr['CRVAL%d'%fits_ind] = crval
    hdr['CRPIX%d'%fits_ind] = 1 

    pyfits.writeto(outname, data, hdr, clobber=True)
    print("Successfully stacked images. Output image is %s"%outname)

    # remove old files
    if not keep_old:
        for fits in fitslist:
            os.system('rm -f %s'%fits)


def substitute_globals(string):
    sub = set(re.findall('\{(.*?)\}', string))
    globs = inspect.currentframe().f_back.f_globals
    if sub:
        for item in map(str, sub):
            string = string.replace("${%s}"%item, globs[item])
        return string
    else:
        return False

