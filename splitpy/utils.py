'''
SUBMODULE utils.py

Module containing utility subroutines

'''

from obspy import UTCDateTime
from numpy import nan,isnan


################################################################################
# Get Options for OTF Request
################################################################################
def get_options():

    from optparse import OptionParser, OptionGroup
    from os.path import exists as exist
    from obspy import UTCDateTime
    from numpy import nan

    parser = OptionParser(usage="Usage: %prog [options] <station database>", description="Script wrapping " \
        "together the python-based implementation of SplitLab by Wustefeld and others. This version " \
        "requests data on the fly for a given date range. Data is requested from the internet using " \
        "the client services framework or from data provided on a local disk. The stations are processed " \
        "one by one with the SKS Splitting parameters measured individually using both the " \
        "Rotation-Correlation (RC) and Silver & Chan (SC) methods.")

    # General Settings
    parser.add_option("--keys", action="store", type="string", dest="stkeys", default="", \
        help="Specify a comma separated list of station keys for which to perform the analysis. These must be " \
        "contained within the station database. Partial keys will be used to match against those in the " \
        "dictionary. For instance, providing IU will match with all stations in the IU network [Default processes " \
        "all stations in the database]")
    parser.add_option("-v", "-V", "--verbose", action="store_true", dest="verb", default=False, \
        help="Specify to increase verbosity.")
    parser.add_option("-O", "--overwrite", action="store_true", dest="ovr", default=False, \
        help="Force the overwriting of pre-existing Split results. Default behaviour prompts for those that " \
        "already exist. Selecting overwrite and skip (ie, both flags) negate each other, and both are set to " \
        "false (every repeat is prompted). [Default False]")
    parser.add_option("-K", "--skip-existing", action="store_true", dest="skip", default=False, \
        help="Skip any event for which existing splitting results are saved to disk. Default behaviour prompts for " \
        "each event. Selecting skip and overwrite (ie, both flags) negate each other, and both are set to " \
        "False (every repeat is prompted). [Default False]")


    # Server Settings
    ServerGroup = OptionGroup(parser, title="Server Settings", description="Settings associated with which " \
        "datacenter to log into.")
    ServerGroup.add_option("-S", "--Server", action="store", type=str, dest="Server", default="IRIS", \
        help="Specify the server to connect to. Options include: BGR, ETH, GEONET, GFZ, INGV, IPGP, IRIS, KOERI, " \
        "LMU, NCEDC, NEIP, NERIES, ODC, ORFEUS, RESIF, SCEDC, USGS, USP. [Default IRIS]")
    ServerGroup.add_option("-U", "--User-Auth", action="store", type=str, dest="UserAuth", default="", \
        help="Enter your IRIS Authentification Username and Password (--User-Auth='username:authpassword') to " \
        "access and download restricted data. [Default no user and password]")

    # Database Settings
    DataGroup = OptionGroup(parser, title="Local Data Settings", description="Settings associated with defining " \
        "and using a local data base of pre-downloaded day-long SAC files.")
    DataGroup.add_option("--local-data", action="store", type="string", dest="localdata", default=None, \
        help="Specify a comma separated list of paths containing day-long sac files of data already downloaded. " \
        "If data exists for a seismogram is already present on disk, it is selected preferentially over downloading " \
        "the data using the Client interface")
    DataGroup.add_option("--no-data-zero", action="store_true", dest="ndval", default=False, \
        help="Specify to force missing data to be set as zero, rather than default behaviour which sets to nan.")
    DataGroup.add_option("--no-local-net", action="store_false", dest="useNet", default=True, \
        help="Specify to prevent using the Network code in the search for local data (sometimes for CN stations " \
        "the dictionary name for a station may disagree with that in the filename. [Default Network used]")

    # Constants Settings
    ConstGroup = OptionGroup(parser, title='Parameter Settings', description="Miscellaneous default values and settings")
    ConstGroup.add_option("--Vp", action="store", type="float", dest="vp", default=6., \
        help="Specify default P velocity value. [Default 6.0 km/s]")
    ConstGroup.add_option("--SNR", action="store", type="float", dest="msnr", default=7.5, \
        help="Specify the SNR threshold used to determine whether events are processedc. [Default 7.5]")
    ConstGroup.add_option("--window", action="store", type="float", dest="dts", default=120., \
        help="Specify time window length before and after the SKS arrival. The total window length is 2*dst. " \
        "[Default 120 s]")
    ConstGroup.add_option("--max-delay", action="store", type="float", dest="maxdt", default=4.,\
        help="Specify the maximum delay time. [Default 4 s]")
    ConstGroup.add_option("--time-increment", action="store", type="float", dest="ddt", default=0.1, \
        help="Specify the time increment. [Default 0.1 s]")
    ConstGroup.add_option("--angle-increment", action="store", type="float", dest="dphi", default=1., \
        help="Specify the angle increment. [Default 1 d]")
    ConstGroup.add_option("--transverse-SNR", action="store", type="float", dest="snrTlim", default=1., \
        help="Specify the minimum SNR Threshold for the Transverse component to be considered Non-Null. [Default 1.]")


    # Event Selection Criteria
    EventGroup = OptionGroup(parser, title="Event Settings", description="Settings associated with refining " \
        "the events to include in matching station pairs")
    EventGroup.add_option("--start-time", action="store", type="string", dest="startT", default="", \
        help="Specify a UTCDateTime compatible string representing the start time for the event search. " \
        "This will override any station start times. [Default more recent start date for each station pair]")
    EventGroup.add_option("--end-time", action="store", type="string", dest="endT", default="", \
        help="Specify a UTCDateTime compatible string representing the start time for the event search. " \
        "This will override any station end times [Default older end date for each the pair of stations]")
    EventGroup.add_option("--reverse-order", "-R", action="store_true", dest="reverse", default=False, \
        help="Reverse order of events. Default behaviour starts at oldest event and works towards most recent. " \
        "Specify reverse order and instead the program will start with the most recent events and work towards older")
    EventGroup.add_option("--min-mag", action="store", type="float", dest="minmag", default=6.0, \
        help="Specify the minimum magnitude of event for which to search. [Default 5.8]")
    EventGroup.add_option("--max-mag", action="store", type="float", dest="maxmag", default=None, \
        help="Specify the maximum magnitude of event for which to search. [Default None, i.e. no limit]")

    # Geometry Settings
    GeomGroup = OptionGroup(parser, title="Geometry Settings", description="Settings associatd with the " \
        "event-station geometries")
    GeomGroup.add_option("--min-dist", action="store", type="float", dest="mindist", default=85., \
        help="Specify the minimum great circle distance (degrees) between the station and event. [Default 85]")
    GeomGroup.add_option("--max-dist", action="store", type="float", dest="maxdist", default=120., \
        help="Specify the maximum great circle distance (degrees) between the station and event. [Default 120]")

    parser.add_option_group(ServerGroup)
    parser.add_option_group(DataGroup)
    parser.add_option_group(EventGroup)
    parser.add_option_group(GeomGroup)
    parser.add_option_group(ConstGroup)
    (opts,args) = parser.parse_args()

    # Check inputs
    if len(args) != 1: parser.error("Need station database file")
    indb = args[0]
    if not exist(indb):
        parser.error("Input file " + indb + " does not exist")

    # create station key list
    if len(opts.stkeys)>0:
        opts.stkeys = opts.stkeys.split(',')

    # construct start time
    if len(opts.startT)>0:
        try:
            opts.startT = UTCDateTime(opts.startT)
        except:
            parser.error("Cannot construct UTCDateTime from start time: " + opts.startT)
    else:
        opts.startT = None

    # construct end time
    if len(opts.endT)>0:
        try:
            opts.endT = UTCDateTime(opts.endT)
        except:
            parser.error("Cannot construct UTCDateTime from end time: " + opts.endT)
    else:
        opts.endT = None

    # Parse User Authentification
    if not len(opts.UserAuth)==0:
        tt = opts.UserAuth.split(':')
        if not len(tt)==2:
            parser.error("Error: Incorrect Username and Password Strings for User Authentification")
        else:
            opts.UserAuth = tt
    else:
        opts.UserAuth = []

    # Check existing file behaviour
    if opts.skip and opts.ovr:
        opts.skip = False
        opts.ovr = False

    # Parse Local Data directories
    if opts.localdata is not None:
        opts.localdata = opts.localdata.split(',')
    else:
        opts.localdata = []

    # Check NoData Value
    if opts.ndval:
        opts.ndval = 0.0
    else:
        opts.ndval = nan

    return (opts, indb)
################################################################################




################################################################################
# Get Options SKS Offline Preparation
################################################################################
def get_options_prep_offline():

    from optparse import OptionParser, OptionGroup
    from os.path import exists as exist
    from obspy import UTCDateTime
    from numpy import nan

    parser = OptionParser(usage="Usage: %prog [options] <station database>", description="Script to " \
        "download and prepare datasets for SKS splitting processing. This script downloads and prepares " \
        "event and station data, so that splitting can then be calculated offline.")

    # General Settings
    parser.add_option("--keys", action="store", type="string", dest="stkeys", default="", \
        help="Specify a comma separated list of station keys for which to perform analysis. These must be " \
        "contained within the station database. Partial keys will be used to match against those in the " \
        "dictionary. For instance, providing IU will match with all stations in the IU network [Default " \
        "processes all stations in the database]")
    parser.add_option("-v", "-V","--verbose", action="store_true", dest="verb", default=False, \
        help="Specify to increase verbosity.")
    parser.add_option("--local-data", action="store", type="string", dest="localdata", default=None, \
        help="Specify a comma separated list of paths containing day-long sac files of data already " \
        "downloaded. If data exists for a seismogram is already present on disk, it is selected " \
        "preferentially over downloading the data using the Client interface")
    parser.add_option("--no-data-zero", action="store_true", dest="ndval", default=False, \
        help="Specify to force missing data to be set as zero, rather than default behaviour which sets to nan.")
    parser.add_option("--no-local-net", action="store_false", dest="useNet", default=True, \
        help="Specify to prevent using the Network code in the search for local data (sometimes for CN " \
        "stations the dictionary name for a station may disagree with that in the filename. [Default Network used]")
    parser.add_option("-D", "--data-directory", action="store", type="string", dest="datadir", default="DATA", \
        help="Specify the directory prefix in which the prepared data is stored. [Default 'DATA']. The start " \
        "and end time and date as well as min and max magnitudes are included in the final folder name.")

    # Server Settings
    ServerGroup = OptionGroup(parser, title="Server Settings", description="Settings associated with which " \
        "datacenter to log into.")
    ServerGroup.add_option("-S", "--Server", action="store", type=str, dest="Server", default="IRIS", \
        help="Specify the server to connect to. Options include: BGR, ETH, GEONET, GFZ, INGV, IPGP, IRIS, " \
        "KOERI, LMU, NCEDC, NEIP, NERIES, ODC, ORFEUS, RESIF, SCEDC, USGS, USP. [Default IRIS]")
    ServerGroup.add_option("-U", "--User-Auth", action="store", type=str, dest="UserAuth", default="", \
        help="Enter your IRIS Authentification Username and Password (--User-Auth='username:authpassword') " \
        "to access and download restricted data. [Default no user and password]")

    # Constants Settings
    ConstGroup = OptionGroup(parser, title='Parameter Settings', description="Miscellaneous default values and settings")
    ConstGroup.add_option("--Vp", action="store", type="float", dest="vp", default=6., \
        help="Specify default P velocity value. [Default 6.0 km/s]")
    ConstGroup.add_option("--SNR", action="store", type="float", dest="msnr", default=7.5, \
        help="Specify the SNR threshold used to determine whether events are processedc. [Default 7.5]")
    ConstGroup.add_option("--window", action="store", type="float", dest="dts", default=120., \
        help="Specify time window length before and after the SKS arrival. The total window length is " \
        "2*dst. [Default 120 s]")
    ConstGroup.add_option("--max-delay", action="store", type="float", dest="maxdt", default=4., \
        help="Specify the maximum delay time. [Default 4 s]")
    ConstGroup.add_option("--time-increment", action="store", type="float", dest="ddt", default=0.1, \
        help="Specify the time increment. [Default 0.1 s]")
    ConstGroup.add_option("--angle-increment", action="store", type="float", dest="dphi", default=1., \
        help="Specify the angle increment. [Default 1 d]")
    ConstGroup.add_option("--transverse-SNR", action="store", type="float", dest="snrTlim", default=1., \
        help="Specify the minimum SNR Threshold for the Transverse component to be considered Non-Null. [Default 1.]")


    # Event Selection Criteria
    EventGroup = OptionGroup(parser, title="Event Settings", description="Settings associated with " \
        "refining the events to include in matching station pairs")
    EventGroup.add_option("--start-time", action="store", type="string", dest="startT", default="", \
        help="Specify a UTCDateTime compatible string representing the start time for the event search. " \
        "This will override any station start times. [Default more recent start date for each station pair]")
    EventGroup.add_option("--end-time", action="store", type="string", dest="endT", default="", \
        help="Specify a UTCDateTime compatible string representing the start time for the event search. " \
        "This will override any station end times [Default older end date for each the pair of stations]")
    EventGroup.add_option("--min-mag", action="store", type="float", dest="minmag", default=5.8, \
        help="Specify the minimum magnitude of event for which to search. [Default 5.8]")
    EventGroup.add_option("--max-mag", action="store", type="float", dest="maxmag", default=None, \
        help="Specify the maximum magnitude of event for which to search. [Default None, ie no limit]")

    # Geometry Settings
    GeomGroup=OptionGroup(parser, title="Geometry Settings", description="Settings associatd with the " \
        "event-station geometries")
    GeomGroup.add_option("--min-dist", action="store", type="float", dest="mindist", default=85., \
        help="Specify the minimum great circle distance (degrees) between the station and event. [Default 85]")
    GeomGroup.add_option("--max-dist", action="store", type="float", dest="maxdist", default=120., \
        help="Specify the maximum great circle distance (degrees) between the station and event. [Default 120]")

    parser.add_option_group(ServerGroup)
    parser.add_option_group(EventGroup)
    parser.add_option_group(GeomGroup)
    parser.add_option_group(ConstGroup)
    (opts,args) = parser.parse_args()

    # Check inputs
    if len(args) != 1: parser.error("Need station database file")
    indb=args[0]
    if not exist(indb):
        parser.error("Input file " + indb + " does not exist")

    # create station key list
    if len(opts.stkeys)>0:
        opts.stkeys = opts.stkeys.split(',')

    # construct start time
    if len(opts.startT)>0:
        try:
            opts.startT = UTCDateTime(opts.startT)
        except:
            parser.error("Cannot construct UTCDateTime from start time: " + opts.startT)
    else:
        opts.startT = None

    # construct end time
    if len(opts.endT)>0:
        try:
            opts.endT = UTCDateTime(opts.endT)
        except:
            parser.error("Cannot construct UTCDateTime from end time: " + opts.endT)
    else:
        opts.endT = None

    # Parse User Authentification
    if not len(opts.UserAuth)==0:
        tt = opts.UserAuth.split(':')
        if not len(tt)==2:
            parser.error("Error: Incorrect Username and Password Strings for User Authentification")
        else:
            opts.UserAuth = tt
    else:
        opts.UserAuth = []

    # Parse Local Data directories
    if opts.localdata is not None:
        opts.localdata = opts.localdata.split(',')
    else:
        opts.localdata = []

    # Check NoData Value
    if opts.ndval:
        opts.ndval = 0.0
    else:
        opts.ndval = nan

    return (opts, indb)
################################################################################




################################################################################
# Get Options SKS Offline Processing
################################################################################
def get_options_OL_proc():

    from optparse import OptionParser, OptionGroup
    from os.path import exists as exist
    from obspy import UTCDateTime
    from numpy import nan

    parser = OptionParser(usage="Usage: %prog [options] <station database>", description="Script to process " \
        "and calculate the spliting parmaters for a dataset that has already been downloaded by sks_prep.py. ")

    # General Settings
    parser.add_option("--keys", action="store", type="string", dest="stkeys", default="", \
        help="Specify a comma separated list of station keys for which to perform analysis. These must be " \
        "contained within the station database. Partial keys will be used to match against those in the " \
        "dictionary. For instance, providing IU will match with all stations in the IU network [Default " \
        "processes all stations in the database]")
#  parser.add_option("-D","--data-directory",action="store",type="string",dest="datadir",default="DATA",help="Specify the directory prefix in which the prepared data is stored. [Default 'DATA']. The start and end time and date as well as min and max magnitudes are included in the final folder name.")

    # Constants Settings
    ConstGroup = OptionGroup(parser, title='Parameter Settings', description="Miscellaneous default values and settings")
    ConstGroup.add_option("--Vp", action="store", type="float", dest="vp", default=6., \
        help="Specify default P velocity value. [Default 6.0 km/s]")
    ConstGroup.add_option("--SNR", action="store", type="float", dest="msnr", default=7.5, \
        help="Specify the SNR threshold used to determine whether events are processedc. [Default 7.5]")
    ConstGroup.add_option("--window", action="store", type="float", dest="dts", default=120., \
        help="Specify time window length before and after the SKS arrival. The total window length is 2*dst. " \
        "[Default 120 s]")
    ConstGroup.add_option("--max-delay", action="store", type="float", dest="maxdt", default=4., \
        help="Specify the maximum delay time. [Default 4 s]")
    ConstGroup.add_option("--time-increment", action="store", type="float", dest="ddt", default=0.1, \
        help="Specify the time increment. [Default 0.1 s]")
    ConstGroup.add_option("--angle-increment", action="store", type="float", dest="dphi", default=1., \
        help="Specify the angle increment. [Default 1 d]")
    ConstGroup.add_option("--transverse-SNR", action="store", type="float", dest="snrTlim", default=1., \
        help="Specify the minimum SNR Threshold for the Transverse component to be considered Non-Null. [Default 1.]")


    # Event Selection Criteria
    EventGroup = OptionGroup(parser, title="Event Settings", description="Settings associated with " \
        "refining the events to include in matching station pairs")
    EventGroup.add_option("--start-time", action="store", type="string", dest="startT", default="", \
        help="Specify a UTCDateTime compatible string representing the start time for the event search. " \
        "This will override any station start times. [Default more recent start date for each station pair]")
    EventGroup.add_option("--end-time", action="store", type="string", dest="endT", default="", \
        help="Specify a UTCDateTime compatible string representing the start time for the event search. " \
        "This will override any station end times [Default older end date for each the pair of stations]")
    EventGroup.add_option("--reverse-order", "-R", action="store_true", dest="reverse", default=False, \
        help="Reverse order of events. Default behaviour starts at oldest event and works towards most " \
        "recent. Specify reverse order and instead the program will start with the most recent events and " \
        "work towards older")
    EventGroup.add_option("--min-mag", action="store", type="float", dest="minmag", default=5.8, \
        help="Specify the minimum magnitude of event for which to search. [Default 5.8]")
    EventGroup.add_option("--max-mag", action="store", type="float", dest="maxmag", default=None, \
        help="Specify the maximum magnitude of event for which to search. [Default None, ie no limit]")

    # Geometry Settings
    GeomGroup = OptionGroup(parser, title="Geometry Settings", description="Settings associatd with " \
        "the event-station geometries")
    GeomGroup.add_option("--min-dist", action="store", type="float", dest="mindist", default=85., \
        help="Specify the minimum great circle distance (degrees) between the station and event. [Default 85]")
    GeomGroup.add_option("--max-dist", action="store", type="float", dest="maxdist", default=120., \
        help="Specify the maximum great circle distance (degrees) between the station and event. [Default 120]")

    parser.add_option_group(EventGroup)
    parser.add_option_group(GeomGroup)
    parser.add_option_group(ConstGroup)
    (opts,args) = parser.parse_args()

    # Check inputs
    if len(args) != 1: parser.error("Need Data Folder")
    indr = args[0]
    if not exist(indr):
        parser.error("Input Data Folder " + indr + " does not exist")

    # create station key list
    if len(opts.stkeys)>0:
        opts.stkeys=opts.stkeys.split(',')

    # construct start time
    if len(opts.startT)>0:
        try:
            opts.startT = UTCDateTime(opts.startT)
        except:
            parser.error("Cannot construct UTCDateTime from start time: " + opts.startT)
    else:
        opts.startT = None

    # construct end time
    if len(opts.endT)>0:
        try:
            opts.endT = UTCDateTime(opts.endT)
        except:
            parser.error("Cannot construct UTCDateTime from end time: " + opts.endT)
    else:
        opts.endT = None

    return (opts, indr)
################################################################################



################################################################################
################################################################################
def parse_localdata_for_comp(comp='Z', stdata=list, sta=None, start=UTCDateTime, end=UTCDateTime, ndval=nan):
    from fnmatch import filter
    from obspy import read
    '''
    Function to determine the path to data for a given component and alternate network
    '''

    # Get start and end parameters
    styr=start.strftime("%Y")
    stjd=start.strftime("%j")
    edyr=end.strftime("%Y")
    edjd=end.strftime("%j")

    # Intialize to default positive error
    erd = True

    print(("*          {0:2s}{1:1s} - Checking Disk".format(sta.channel.upper(),comp.upper())))

    # Time Window Spans Single Day
    if stjd==edjd:
        # Format 1
        lclfiles = list(filter(stdata, '*/{0:4s}.{1:3s}.{2:s}.{3:s}.*.{4:2s}{5:1s}.SAC'.format( \
                 styr, stjd, sta.network.upper(), sta.station.upper(), sta.channel.upper()[0:2], \
                 comp.upper())))
        # Format 2
        if len(lclfiles)==0:
            lclfiles = list(filter(stdata, '*/{0:4s}.{1:3s}.{2:s}.{3:s}.*.*{4:1s}.SAC'.format( \
                     styr, stjd, sta.network.upper(), sta.station.upper(), comp.upper())))
        # Alternate Nets (for CN/PO issues) Format 1
        if len(lclfiles)==0:
            lclfiles = []
            for anet in sta.altnet:
                lclfiles.extend(list(filter(stdata, '*/{0:4s}.{1:3s}.{2:s}.{3:s}.*.{4:2s}{5:1s}.SAC'.format( \
                        styr, stjd, anet.upper(), sta.station.upper(), sta.channel.upper()[0:2],    \
                        comp.upper()))))

        # Alternate Nets (for CN/PO issues) Format 2
        if len(lclfiles)==0:
            # Check Alternate Networks
            lclfiles = []
            for anet in sta.altnet:
                lclfiles.extend(list(filter(stdata, '*/{0:4s}.{1:3s}.{2:s}.{3:s}.*.*{4:1s}.SAC'.format( \
                        styr, stjd, sta.network.upper(), sta.station.upper(), comp.upper()))))

        # If still no Local files stop
        if len(lclfiles)==0:
            print("*              - Data Unavailable")
            return erd, None

        # Process the local Files
        for sacfile in lclfiles:
            # Read File
            st = read(sacfile, format="SAC")

            # Should only be one component, otherwise keep reading If more than 1 component, error
            if len(st)!=1:
                pass

            else:
                # Check for NoData and convert to NaN
                stnd = st[0].stats.sac['user9']
                eddt = False
                if (not stnd == 0.0) and (not stnd == -12345.0):
                    st[0].data[st[0].data==stnd] = ndval
                    eddt = True

                # Check start/end times in range
                if st[0].stats.starttime<=start and st[0].stats.endtime >=end:
                    st.trim(starttime=start, endtime=end)

                    # Check for Nan in stream
                    if True in isnan(st[0].data):
                        print("*          !!! Missing Data Present !!! Skipping (NaNs)")
                    else:
                        if eddt and (ndval == 0.0):
                            if any(st[0].data==0.0):
                                print("*          !!! Missing Data Present !!! (Set to Zero)")

                        st[0].stats.update()
                        tloc = st[0].stats.location
                        if len(tloc)==0: tloc = "--"

                        # Processed succesfully...Finish
                        print(("*          {1:3s}.{2:2s}  - From Disk".format(\
                            st[0].stats.station,st[0].stats.channel.upper(),tloc  )))
                        return False, st


    # Time Window spans Multiple days
    else:
        # Day 1 Format 1
        lclfiles1 = list(filter(stdata, '*/{0:4s}.{1:3s}.{2:s}.{3:s}.*.{4:2s}{5:1s}.SAC'.format( \
                    styr, stjd, sta.network.upper(), sta.station.upper(), sta.channel.upper()[0:2], \
                    comp.upper())))
        # Day 1 Format 2
        if len(lclfiles1)==0:
            lclfiles1 = list(filter(stdata, '*/{0:4s}.{1:3s}.{2:s}.{3:s}.*.*{4:1s}.SAC'.format( \
                        styr, stjd, sta.network.upper(), sta.station.upper(), comp.upper())))
        # Day 1 Alternate Nets (for CN/PO issues) Format 1
        if len(lclfiles1)==0:
            lclfiles1 = []
            for anet in sta.altnet:
                lclfiles1.extend(list(filter(stdata, '*/{0:4s}.{1:3s}.{2:s}.{3:s}.*.{4:2s}{5:1s}.SAC'.format( \
                                 styr, stjd, anet.upper(), sta.station.upper(), sta.channel.upper()[0:2],    \
                                 comp.upper()))))
        # Day 1 Alternate Nets (for CN/PO issues) Format 2
        if len(lclfiles1)==0:
            lclfiles1 = []
            for anet in sta.altnet:
                lclfiles1.extend(list(filter(stdata, '*/{0:4s}.{1:3s}.{2:s}.{3:s}.*.*{4:1s}.SAC'.format( \
                                 styr, stjd, anet.upper(), sta.station.upper(), comp.upper()))))

        # Day 2 Format 1
        lclfiles2 = list(filter(stdata, '*/{0:4s}.{1:3s}.{2:s}.{3:s}.*.{4:2s}{5:1s}.SAC'.format( \
                    edyr, edjd, sta.network.upper(), sta.station.upper(), sta.channel.upper()[0:2], \
                    comp.upper())))
        # Day 2 Format 2
        if len(lclfiles2)==0:
            lclfiles2 = list(filter(stdata, '*/{0:4s}.{1:3s}.{2:s}.{3:s}.*.*{4:1s}.SAC'.format(\
                        edyr, edjd, sta.network.upper(), sta.station.upper(), comp.upper())))
        # Day 2 Alternate Nets (for CN/PO issues) Format 1
        if len(lclfiles2)==0:
            lclfiles2 = []
            for anet in sta.altnet:
                lclfiles2.extend(list(filter(stdata, '*/{0:4s}.{1:3s}.{2:s}.{3:s}.*.{4:2s}{5:1s}.SAC'.format( \
                                 edyr, edjd, anet.upper(), sta.station.upper(), sta.channel.upper()[0:2],\
                                 comp.upper()))))
        # Day 2 Alternate Nets (for CN/PO issues) Format 2
        if len(lclfiles2)==0:
            lclfiles2 = []
            for anet in sta.altnet:
                lclfiles2.extend(list(filter(stdata, '*/{0:4s}.{1:3s}.{2:s}.{3:s}.*.*{4:1s}.SAC'.format(\
                                edyr, edjd, anet.upper(), sta.station.upper(), comp.upper()))))

        # If still no Local files stop
        if len(lclfiles1)==0 and len(lclfiles2)==0:
            print("*              - Data Unavailable")
            return erd, None

        # Now try to merge the two separate day files
        if len(lclfiles1)>0 and len(lclfiles2)>0:
            # Loop over first day file options
            for sacf1 in lclfiles1:
                st1 = read(sacf1, format='SAC')
                # Loop over second day file options
                for sacf2 in lclfiles2:
                    st2 = read(sacf2, format='SAC')

                    # Check time overlap of the two files.
                    if st1[0].stats.endtime >= st2[0].stats.starttime - st2[0].stats.delta:
                        # Check for NoData and convert to NaN
                        st1nd = st1[0].stats.sac['user9']
                        st2nd = st2[0].stats.sac['user9']
                        eddt1 = False
                        eddt2 = False
                        if (not st1nd == 0.0) and (not st1nd == -12345.0):
                            st1[0].data[st1[0].data==st1nd] = ndval
                            eddt1 = True
                        if (not st2nd == 0.0) and (not st2nd == -12345.0):
                            st2[0].data[st2[0].data==st2nd] = ndval
                            eddt2 = True

                        st = st1 + st2
                        try:  # Need to work on this HERE (AJS OCT 2015). If Calibration factors are different, then the traces cannot be merged.
                            st.merge()

                            # Should only be one component, otherwise keep reading If more than 1 component, error
                            if len(st)!=1:
                                print(st)
                                print("merge failed?")

                            else:
                                if st[0].stats.starttime<=start and st[0].stats.endtime>=end:
                                    st.trim(starttime=start, endtime=end)

                                    # Check for Nan in stream
                                    if True in isnan(st[0].data):
                                        print("*          !!! Missing Data Present !!! Skipping (NaNs)")
                                    else:
                                        if (eddt1 or eddt2) and (ndval == 0.0):
                                            if any(st[0].data==0.0):
                                                print("*          !!! Missing Data Present !!! (Set to Zero)")

                                        st[0].stats.update()
                                        tloc = st[0].stats.location
                                        if len(tloc)==0: tloc = "--"

                                        # Processed succesfully...Finish
                                        print(("*          {1:3s}.{2:2s}  - From Disk".format(\
                                            st[0].stats.station, st[0].stats.channel.upper(), tloc  )))
                                        return False, st

                        except:
                            pass
                    else:
                        print(("*                 - Merge Failed: No Overlap {0:s} - {1:s}".format(\
                            st1[0].stats.endtime, st2[0].stats.starttime - st2[0].stats.delta)))

    # If we got here, we did not get the data.
    print("*              - Data Unavailable")
    return erd, None
################################################################################



################################################################################
################################################################################
def get_data_NEZ(client=None, sta=None, start=UTCDateTime, end=UTCDateTime, stdata=list, ndval=nan):

    from fnmatch import filter
    from obspy import read
    from os.path import dirname, join, exists
    from numpy import any
    '''
    Function to build a stream object for a seismogram in a given time window either
    by downloading data from the client object or alternatively first checking if the
    given data is already available locally.

    Currently only supports NEZ Components!!!
    '''
    # Output
    print(("*     {0:s}.{1:2s} - NEZ:".format(sta.station, sta.channel.upper())))

    # Set Error Default to True
    erd = True

    # Check if there is local data
    if len(stdata)>0:
        # Only a single day: Search for local data
        # Get Z localdata
        errZ, stZ = parse_localdata_for_comp(comp='Z', stdata=stdata, sta=sta, start=start, end=end, ndval=ndval)
        # Get N localdata
        errN, stN = parse_localdata_for_comp(comp='N', stdata=stdata, sta=sta, start=start, end=end, ndval=ndval)
        # Get E localdata
        errE, stE = parse_localdata_for_comp(comp='E', stdata=stdata, sta=sta, start=start, end=end, ndval=ndval)
        # Retreived Succesfully?
        erd = errZ or errN or errE
        if not erd:
            # Combine Data
            st = stZ + stN + stE

    # No local data? Request using client
    if erd:
        erd = False

        for loc in sta.location:
            tloc = loc
            # Constract location name
            if len(tloc)==0: tloc = "--"
            # Construct Channel List
            channels = sta.channel.upper() + 'E,' + sta.channel.upper() + 'N,' + sta.channel.upper() + 'Z'
            print(("*          {1:2s}[ENZ].{2:2s} - Checking Network".format(sta.station, sta.channel.upper(), tloc)))
            try:
                st = client.get_waveforms(network=sta.network, station=sta.station, location=loc, \
                    channel=channels, starttime=start, endtime=end, attach_response=False)
                if len(st)==3:
                    erd = False
                    print("*             - Data Downloaded")
                else:
                    erd = True
                    st = None
                    print("*             - Data Unavailable")
            except:
                erd = True
                st = None
                print("*             - Data Unavailable")

            # Break if we successfully obtained 3 components in st
            if not erd:
                break


    # Check the correct 3 components exist
    if st is None:
        print("* Error retrieving waveforms")
        print("****************************************************")
        return True, None, None, None
    elif not st.select(component='Z')[0] or not st.select(component='E'[0]) or not st.select(component='N')[0]:
        print("* Error retrieving waveforms")
        if not st.select(component='Z')[0]: print("*   --Z Missing")
        if not st.select(component='E')[0]: print("*   --E Missing")
        if not st.select(component='N')[0]: print("*   --N Missing")
        print("****************************************************")
        return True, None, None, None

    # Three components successfully retrieved
    print("* Waveforms Retrieved...")

    # Check trace lengths
    ll0 = len(st.select(component='Z')[0].data)
    ll1 = len(st.select(component='E')[0].data)
    ll2 = len(st.select(component='Z')[0].data)
    if not (ll0 == ll1 and ll0 == ll2):
        print(("* Error:  Trace lengths (Z,E,N): ",ll0,ll1,ll2))
        print("****************************************************")
        return True, None, None, None

    # Detrend data
    st.detrend('demean'); st.detrend('linear')

    # Filter Traces
    st.filter('lowpass',freq=0.5*5.0, corners=2, zerophase=True)
    st.resample(5.0)
    st.filter('bandpass', freqmin=0.01, freqmax=0.25, corners=2, zerophase=True)

    # Extract traces
    trE = st.select(component='E')[0]
    trN = st.select(component='N')[0]
    trZ = st.select(component='Z')[0]

    # Return Flag and Data
    return False, trN, trE, trZ
################################################################################
