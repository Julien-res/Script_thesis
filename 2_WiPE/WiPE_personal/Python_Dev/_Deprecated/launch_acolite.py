## Simplified ACOLITE launcher for direct Python execution (no GUI), modified from ACOLITE wrapper of QV
def launch_acolite(settings=None, settings_agh=None, inputfile=None, output=None, sensor=None):
    ## Need to run freeze_support for PyInstaller binary generation
    from multiprocessing import freeze_support
    freeze_support()

    ## Import necessary modules
    import os
    import datetime

    ## Import acolite source
    try:
        import acolite as ac
    except ImportError:
        print('Could not import ACOLITE source')
        return

    try:
        from osgeo import ogr, osr, gdal
    except ImportError:
        print('Could not import osgeo')
        return

    ## Fix matplotlib backend to Agg
    import matplotlib
    matplotlib.use("Agg")

    ## Run AGH if settings_agh is provided
    if settings_agh is not None:
        import acolite.gee
        acolite.gee.agh_run(settings=settings_agh, acolite_settings=settings)
        return

    ## Command line processing, run acolite_run directly
    time_start = datetime.datetime.now()  # Time of processing start

    ## Parse inputfile and output
    inputfile_list = inputfile.split(',') if inputfile else None

    ## Check for settings file
    if settings is None:
        print('No settings file given')
        return
    if not os.path.exists(settings):
        print(f'Settings file {settings} does not exist.')
        return

    ## Run processing
    ac.acolite.acolite_run(settings, inputfile=inputfile_list, output=output)
