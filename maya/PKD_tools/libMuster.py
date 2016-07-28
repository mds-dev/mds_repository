import subprocess
from PKD_tools import libCrypto
from PKD_tools import libFile

import pymel.core as pm
import getpass


class MusterAPI(object):
    def __init__(self):
        # Initialise the muster class

        # Set the app path
        self.appPath = r"C:\apps\muster\8.6.0\Mrtool".strip()

        # Login details
        self.ip = "10.0.0.21"
        self.port = "9781"
        self.username = "admin"
        self.encyptedPwd = "w9rl6MrqnaY="
        self._pwd_ = ''
        # Cmd line
        self._cmdline_ = ""
        # Defaults settings
        # By frame
        self._byframe_ = 1
        # Set the pool
        self._pool_ = "BOAD - Vray"
        # Set the images folder
        self._images_folder_ = r"\\productions\boad\Pipeline\tools\maya\rendering\Images"
        # Start frame
        self._startframe_ = None
        # End Frame
        self._endframe_ = None
        # Set the project foldeer
        self._project_folder_ = r"\\productions\boad\Pipeline\tools\maya\rendering"
        # #Set the project
        # does not work
        # self.cmdline = "-project ABC"
        # Set the Name
        self._jobname_ = "TestingSubmitMaya_ABC"
        # Set the Packet Size
        self._packetsize_ = 4
        # Set the max instances
        self._instances_ = 20
        # Set the priority
        self._priority_ = 1

        # Set the priority
        self._file_name_ = 20

    def initialise_muster(self, mode="-b"):
        # Initialise the Muster tool
        self._cmdline_ = self.appPath.strip()
        self.cmdline = mode
        self.cmdline = "-s " + self.ip
        self.cmdline = "-port " + self.port
        self.cmdline = '-u %s' % self.username
        self.cmdline = "-p %s" % self.pwd

    def get_pools(self):
        self.initialise_muster(mode="-q p")
        # Build the query command for the pools
        self.cmdline = "-H 0 -S 0 -pf parent"

        pools = self.execute_cmd()

        for i in range(len(pools)):
            if not len(pools[i]):
                pools[i] = "Entire Farm"
            pools[i] = pools[i].strip()

        return pools

    def get_engines(self):
        self.initialise_muster(mode="-q t")
        # Build the query command for the pools
        self.cmdline = "-H 0 -S 0 -pf parent"

        pools = self.execute_cmd()

        for i in range(len(pools)):
            pools[i] = pools[i].strip()

        return pools

    def execute_cmd(self):
        p = subprocess.Popen(self.cmdline, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        output = []
        for line in p.stdout.readlines():
            line = line.replace("\r\n", "")
            if line not in output:
                output.append(line)
        retval = p.wait()
        # print self.cmdline
        return output

    def send_to_farm(self):
        # Render Globals
        # Get the folder
        self.initialise_muster()

        # Set the start frame
        self.cmdline = self.startframe

        # Set the end frame
        self.cmdline = self.endframe

        # By frame
        self.cmdline = self.byframe

        # Maya defeals
        self.cmdline = "-attr MAYADIGITS 4 0 -se 1 -st 1"

        # Set the Vray engine
        self.cmdline = '-e 37'

        # Set the pool
        self.cmdline = self.pool

        # Set the priority
        self.cmdline = self.priority

        # Set the Packet Size
        self.cmdline = self.packetsize

        # Set the max instances
        self.cmdline = self.instances

        # Set the Name

        self.cmdline = self.jobname

        # Set the Department name
        self.cmdline = self.department


        # Set the scene name
        self.cmdline = self.filename

        # Set the images foldeer
        self.cmdline = self.project_folder

        # Set the images foldeer
        self.cmdline = self.images_folder

        # #Set the project
        # self.cmdline = "-project ABC"


        # Set the batch submit
        output = self.execute_cmd()
        return output

    @property
    def pwd(self):
        # Set the password
        if not self._pwd_:
            if self.username == "admin":
                self._pwd_ = libCrypto.decode("muster", self.encyptedPwd)
            else:
                raise Exception("Password not defined")
        return self._pwd_

    @pwd.setter
    def pwd(self, pwd):
        # Set the password
        self._pwd_ = pwd

    @property
    def cmdline(self):
        return self._cmdline_

    @cmdline.setter
    def cmdline(self, newdata):
        # Add to command line
        self._cmdline_ = " %s %s" % (self._cmdline_, newdata)

    @property
    def startframe(self):
        if self._startframe_ is None:
            self._startframe_ = pm.playbackOptions(q=1, ast=1)
        return "-sf %i" % self._startframe_

    @startframe.setter
    def startframe(self, newdata):
        self._startframe_ = int(newdata)

    @property
    def endframe(self):
        if self._endframe_ is None:
            self._endframe_ = pm.playbackOptions(q=1, aet=1)
        return "-ef %i" % self._endframe_

    @endframe.setter
    def endframe(self, newdata):
        self._endframe_ = int(newdata)

    @property
    def byframe(self):
        return "-bf %i" % self._byframe_

    @byframe.setter
    def byframe(self, newdata):
        self._byframe_ = int(newdata)

    @property
    def packetsize(self):
        return "-pk %i" % self._packetsize_

    @packetsize.setter
    def packetsize(self, newdata):
        self._packetsize_ = int(newdata)

    @property
    def priority(self):
        return "-pr %i" % self._priority_

    @priority.setter
    def priority(self, newdata):
        self._priority_ = int(newdata)

    @property
    def instances(self):
        return "-max %i" % self._instances_

    @instances.setter
    def instances(self, newdata):
        self._instances_ = int(newdata)

    @property
    def pool(self):
        return '-pool "%s"' % self._pool_

    @pool.setter
    def pool(self, newdata):
        self._pool_ = newdata

    @property
    def images_folder(self):
        return '-dest "%s"' % self._images_folder_

    @images_folder.setter
    def images_folder(self, newdata):
        self._images_folder_ = libFile.windows_path(newdata)

    @property
    def project_folder(self):
        # Set the project foldeer
        return '-proj "%s"' % self._project_folder_

    @project_folder.setter
    def project_folder(self, newdata):
        self._project_folder_ = libFile.windows_path(newdata)

    @property
    def filename(self):
        if not self._file_name_:
            self._file_name_ = libFile.windows_path(pm.sceneName())
        return '-f "%s"' % self._file_name_

    @filename.setter
    def filename(self, filename):

        self._file_name_ = filename

    @property
    def jobname(self):
        # '-n TestingSubmitMaya_ABC'
        return '-n "%s"' % self._jobname_

    @jobname.setter
    def jobname(self, newdata):
        self._jobname_ = newdata

    @property
    def department(self):
        username = getpass.getuser()
        return '-department "%s"' % username

# api = MusterAPI()
# api.username = "BAD15023"
# api.pwd = "BAD15023"
# #api.test_submit_render()
# print api.get_pools()
# print api.get_engines()


# for stuff in api.get_engines():
#     print stuff
