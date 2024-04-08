
import os
import sys
import optparse
from lvl1_msi import Level1_MSI
from ancillary import Ancillary_NASA


class OptionParser (optparse.OptionParser):
    '''Parse options'''
    def check_required(self, opt):
        option = self.get_option(opt)

        # Assumes the option's 'default' is set to None!
        if getattr(self.values, option.dest) is None:
            self.error(f"{option} option not supplied")
if len(sys.argv) == 1:
    prog = os.path.basename(sys.argv[0])
    print('      ' + sys.argv[0] + ' [options]')
    print("     Aide : ", prog, " --help")
    print("        ou : ", prog, " -h")
    sys.exit(-1)
else:
    USAGE = "usage: %prog [options] "
    parser = OptionParser(usage=USAGE)

    parser.add_option("-i", "--input", dest="input_file", action="store", type="string",
                      help="input (str): path of input datas (MSI-L1C)", 
                      default=None)
    parser.add_option("-o", "--output", dest="output_file", action="store", type="string",
                      help="output (str): Path where output datas",
                      default=None)

    (options, args) = parser.parse_args()

Level1_MSI(options.input_file,ancillary=Ancillary_NASA(directory=options.output_file))