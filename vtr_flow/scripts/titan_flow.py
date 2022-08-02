#!/usr/bin/python
__version__ =   """
                titan_flow.py
                """

###########################################################
# This script is tightly coupled with the q2_flow.tcl
# script (which actually runs Quartus and generates the 
# VQM file).  The q2_flow.tcl script is called from
# this script with the appropriate options
###########################################################

import sys
import argparse
import subprocess
import os
from os import path
from time import time

#Used by push/pop timer
g_timer_stack = []

def main():
    """
    The main function
    """

    #Argument parsing
    args = parse_args()
    args = check_args(args)
    
    push_timer('titan_flow.py script')

    push_timer('VQM Synthesis and BLIF Conversion')
    
    gen_vqm(args)

    gen_blif(args, vqm_file=args.vqm_file, arch_file=args.arch_file, out_file=args.blif_file)
    gen_blif(args, vqm_file=args.vqm_file, arch_file=args.arch_file, out_file=args.eblif_file, eblif_format=True)
    
    pop_timer('VQM Synthesis and BLIF Conversion')
    
    if args.run_sta_map:
        run_sta(args, after_map=True)

    if args.run_fit or args.run_fast_fit:
        run_fit(args)

        if args.gen_post_fit_netlist:
            gen_blif(args, vqm_file=args.vqm_post_fit_file, arch_file=args.arch_file, out_file=args.blif_post_fit_file)
            gen_blif(args, vqm_file=args.vqm_post_fit_file, arch_file=args.arch_file, out_file=args.eblif_post_fit_file, eblif_format=True)
    
    if args.run_sta_fit:
        run_sta(args)

    if args.run_vpr:
        run_vpr(args)


    print ""
    pop_timer('titan_flow.py script')

def parse_args():
    description="""\
    Runs the Titan flow on the specified Quartus 2 Project to generate a BLIF file.

    By default, the quartus project is compiled in its directory, and the
    vqm and blif files are generated in the directory where this script is called.


    The overall flow is as follows:
        1) Synthesize the given QUARTUS_PROJECT with quartus_map
        2) Dump the .vqm file from Quartus
        3) Run vqm2blif to convert the .vqm to .blif
        4) (Optional) Run quartus_fit or quartus_sta
        5) (Optional) Run vpr

    """

    parser = argparse.ArgumentParser(usage="%(prog)s [-h] -q QUARTUS_PROJECT -a ARCH_FILE [--sta_map] [--fit] [--sta_fit] [--vpr] [other options]",
                                    description=description)

    parser.add_argument('--version', action='version', version=__version__,
                        help='Version information')

    #Options effecting quartus operation
    quartus_options = parser.add_argument_group('quartus options')

    quartus_options.add_argument('-q', '--quartus_project', dest='quartus_project', action='store',
                        required=True,
                        help='The Quartus 2 project file of the design to be used')

    quartus_options.add_argument('-f', '--family', dest='device_family', action='store',
                        default='stratixiv',
                        help='The device family to target in Quartus II (default: %(default)s)')

    quartus_options.add_argument('--no_resynth', dest='do_resynthesis', action='store_false',
                        default=True,
                        help='If the vqm output file already exists, do not re-run Quartus II to re-synthesize it')

    
    quartus_options.add_argument('-r', '--report_dir', dest='report_dir', action='store',
                        default='q2_out',
                        help='Force quartus to put reports in a special directory (default: %(default)s)')
    
    quartus_options.add_argument('--sta_map', dest='run_sta_map', action='store_true',
                        default=False,
                        help='Run quartus_sta after quartus_map')
    
    quartus_options.add_argument('--fit', dest='run_fit', action='store_true',
                        default=False,
                        help='Run quartus_fit after synthesis and VQM dumping')
    
    quartus_options.add_argument('--fast_fit', dest='run_fast_fit', action='store_true',
                        default=False,
                        help='Run quartus_fit in fast mode after synthesis and VQM dumping')

    quartus_options.add_argument('--sta_fit', dest='run_sta_fit', action='store_true',
                        default=False,
                        help='Run quartus_sta after quaruts_fit')

    quartus_options.add_argument('--gen_post_fit_netlist', dest='gen_post_fit_netlist', action='store_true',
                        default=False,
                        help='Generate a post-fitting VQM file')

    #Options effecting vqm2blif operation
    vqm2blif_options = parser.add_argument_group('vqm2blif options')

    vqm2blif_options.add_argument('-b', '--blif', dest='blif_file', action='store',
                        help='The output blif file name (default: <project>_<family>.blif')

    vqm2blif_options.add_argument('-e', '--eblif', dest='eblif_file', action='store',
                        help='The output eblif file name (default: <project>_<family>.eblif')

    vqm2blif_options.add_argument('-v', '--vqm', dest='vqm_file', action='store',
                        help='The output vqm file name (default: <project>_<family>.vqm)')

    vqm2blif_options.add_argument('--post_fit_vqm', dest='vqm_post_fit_file', action='store',
                        help='The post-fit output vqm file name (default: <project>_<family>_post_fit.vqm)')

    vqm2blif_options.add_argument('--post_fit_blif', dest='blif_post_fit_file', action='store',
                        help='The post-fit output eblif file name (default: <project>_<family>_post_fit.blif)')

    vqm2blif_options.add_argument('--post_fit_eblif', dest='eblif_post_fit_file', action='store',
                        help='The post-fit output vqm file name (default: <project>_<family>_post_fit.eblif)')

    vqm2blif_options.add_argument('-a', '--arch', dest='arch_file', action='store',
                        required=True,
                        help='The architecture file to use')

    vqm2blif_options.add_argument('--vqm2blif_opts', dest='vqm2blif_extra_opts', action='store',
                        default='-luts vqm', #Outputs blackbox primitives only (no blif .names)
                        help='Provide additional options to vqm2blif as a string (default: "%(default)s")')


    #Options effecting vpr operation
    vpr_options = parser.add_argument_group('vpr options')

    vpr_options.add_argument('--vpr', dest='run_vpr', action='store_true',
                            default=False,
                            help='Run vpr on the generated blif file (default: %(default)s)')

    vpr_options.add_argument('--vpr_opts', dest='vpr_opts', action='store',
                            default="--nodisp --route_chan_width 300",
                            help='Provide additional options to vpr as a string (default: "%(default)s")')


    #External tool location overrides
    exec_options = parser.add_argument_group('external tool override options')
    
    exec_options.add_argument('--titan_dir', dest='titan_dir', action='store',
                              help="Override the default titan directory, used to find the 'vqm2blif' executable (default: TITAN_BASE_DIR environment variable)")

    exec_options.add_argument('--vqm2blif_dir', dest='vqm2blif_dir', action='store',
                              help="Override the default vqm2blif directory, used to find the 'vqm2blif' executable (default: VQM2BLIF_BASE_DIR environment variable)")

    exec_options.add_argument('--quartus_dir', dest='quartus_dir', action='store',
                              help="Override the default quartus binary directory, used to find the 'quartus_sh' executable (default: QII_BASE_DIR environment variable)")

    exec_options.add_argument('--vpr_dir', dest='vpr_dir', action='store',
                              help="Override the default vpr directory, used to find the 'vpr' executable. Only required if running vpr from this script (default: VPR_BASE_DIR environment variable)")

    #Actually evaluate the arguments
    args = parser.parse_args()

    #Print out how the program was run
    print ' '.join(sys.argv)

    return args

def check_args(args):
    """
        Verifies arguments and sets some defaults that can not be easily computed
        in the main argument parser
    """
    #Query environment for base directories if not specified
    # Order of priority is as follows
    #   1) Command-line option
    #   2) Environment variable
    #   3) Inferred from assumed titan directory structure (if applicable)
    if not args.titan_dir:
        titan_env_var = 'TITAN_BASE_DIR'
        try:
            args.titan_dir = os.environ[titan_env_var]
        except KeyError:
            #Try to infer from where this script is located
            inferred_titan_dir = infer_titan_base_dir()
            if inferred_titan_dir != None:
                #Found it
                args.titan_dir = inferred_titan_dir
            else:
                raise ValueError, "could not find titan directory based on %s environment variable, commandline option or from script directory" % titan_env_var
    #Depending on how the path is provided, we might need to expand the user (i.e. '~') or variables
    args.titan_dir = path.expanduser(args.titan_dir)
    args.titan_dir = path.expandvars(args.titan_dir)

    if not args.vqm2blif_dir:
        vqm2blif_env_var = 'VQM2BLIF_BASE_DIR'
        try:
            args.vqm2blif_dir = os.environ[vqm2blif_env_var]
        except KeyError:
            if not args.titan_dir:
                raise ValueError, "could not find vqm2blif directory based on %s environment variable, command line option, or from titan base dir" % vqm2blif_env_var
            else:
                args.vqm2blif_dir = os.path.join(args.titan_dir, 'vqm_to_blif')
    args.vqm2blif_dir = path.expanduser(args.vqm2blif_dir)
    args.vqm2blif_dir = path.expandvars(args.vqm2blif_dir)

    if not args.quartus_dir:
        try:
            args.quartus_dir = os.environ['QII_BASE_DIR']
        except KeyError:
            raise ValueError, "could not find Quartus II binary directory based on QII_BASE_DIR environment variable or command line option" 
    args.quartus_dir = path.expanduser(args.quartus_dir)
    args.quartus_dir = path.expandvars(args.quartus_dir)

    #Only if we are trying to run VPR do we need to find the executable
    if args.run_vpr:
        if not args.vpr_dir:
            try:
                args.vpr_dir = os.environ['VPR_BASE_DIR']
            except KeyError:
                raise ValueError, "could not find vpr directory based on VPR_BASE_DIR environment variable or command line option"
        args.vpr_dir = path.expanduser(args.vpr_dir)
        args.vpr_dir = path.expandvars(args.vpr_dir)

    if args.gen_post_fit_netlist and not (args.run_fit or args.run_fast_fit):
        raise ValueError("Must run fitting to generate a post-fit netlist")

    #Generate default filenames if not specified
    if not args.vqm_file:
        args.vqm_file = path.splitext(path.basename(args.quartus_project))[0] + '_' + args.device_family + '.vqm'

    if not args.blif_file:
        args.blif_file = path.splitext(path.basename(args.quartus_project))[0] + '_' + args.device_family + '.blif'

    if not args.eblif_file:
        args.eblif_file = path.splitext(path.basename(args.quartus_project))[0] + '_' + args.device_family + '.eblif'


    if not args.vqm_post_fit_file:
        args.vqm_post_fit_file = path.splitext(path.basename(args.quartus_project))[0] + '_' + args.device_family + '_post_fit.vqm'

    if not args.blif_post_fit_file:
        args.blif_post_fit_file = path.splitext(path.basename(args.quartus_project))[0] + '_' + args.device_family + '_post_fit.blif'

    if not args.eblif_post_fit_file:
        args.eblif_post_fit_file = path.splitext(path.basename(args.quartus_project))[0] + '_' + args.device_family + '_post_fit.eblif'

    print_config_summary(args)

    return args

def infer_titan_base_dir():
    """
    Tries to figure out if this is a valid titan release directory,
    based on the scripts calling location.

    It checks that:
        1) the scripts calling direcotry is named 'scripts'
        2) the parent directory of the callin directory contains:
            'arch', 'benchmarks', 'scirpts', and 'vqm2blif' directories
    """
    #argv[0] is the relative (or absolute) path to the current script
    # Turn it into an absolute path
    script_path = path.abspath(sys.argv[0])

    script_dir = path.dirname(script_path)
    parent_dir = path.dirname(script_dir)

    #If this is a valid titan release directory, then this script should
    # be located in the following directory
    titan_script_dirname = 'scripts'

    script_dirname_valid = (os.path.basename(script_dir) == titan_script_dirname)

    #Also, the parent directory should contain the following
    titan_dirs = ['arch', 'benchmarks', 'scripts', 'vqm_to_blif']

    #Get the directories in the parent directory
    # walk recursively walks the tree, calling next()
    # generates the list of the current directory
    # which is a tuple of (dirpath, dirnames, filenames)
    # we get the dirnames by grabbing the list at index 1
    parent_dirs = os.walk(parent_dir).next()[1]

    parent_dirs_valid = True
    for dirname in titan_dirs:
        if dirname not in parent_dirs:
            parent_dirs_valid = False

    if parent_dirs_valid and script_dirname_valid:
        #We can assume that this truly is a titan release
        # directory
        return parent_dir #The titan directory
    else:
        return None

def print_config_summary(args):
    print "Path and Directory Configuration:"
    print "  Titan        Dir: %s" % args.titan_dir
    print "  Quartus II   Dir: %s" % args.quartus_dir
    print "  VQM2BLIF     Dir: %s" % args.vqm2blif_dir
    if args.run_vpr:
        print "  VPR          Dir: %s" % args.titan_dir
    print "  VQM Output  File: %s" % args.vqm_file
    print "  BLIF Output File: %s" % args.blif_file

def gen_vqm(args):
    """
    Generates a vqm file from a quartus project
    using quartus_sh
    """
    push_timer("Generating VQM")

    #Absolute path to vqm file, so it ends up in the script run directory
    args.vqm_file = path.join(os.getcwd(), args.vqm_file)

    #Re-synthesize if told so, or if the file doesn't exist
    if args.do_resynthesis or not path.isfile(args.vqm_file):


        #Quartus Verilog to VQM conversion script
        q2_flow_tcl = path.join(args.titan_dir, 'scripts/q2_flow.tcl')

        q2_shell = path.join(args.quartus_dir, 'quartus_sh')
        q2_cmd = [q2_shell,
                    '--64bit',
                    '-t',               q2_flow_tcl,
                    '-project',         args.quartus_project,
                    '-family',          args.device_family,
                    '-synth',
                    '-report_dir',      args.report_dir,
                    '-vqm_out_file',    args.vqm_file]

        #Verilog to vqm conversion
        call_cmd("\nINFO: Calling Quartus", "ERROR: VQM generation failed", q2_cmd)


    else:
        print "INFO: found existing VQM file, not re-synthesizing"

    pop_timer("Generating VQM")
    

def gen_blif(args, arch_file, vqm_file, out_file, eblif_format=False):
    """
    Converts a vqm file to a blif file
    using vqm2blif
    """
    push_timer("Converting VQM to BLIF")

    #VQM to blif conversion
    vqm2blif_exec = path.join(args.vqm2blif_dir, 'vqm2blif')

    vqm2blif_cmd = [vqm2blif_exec,
                    '-arch',    arch_file,
                    '-vqm',     vqm_file,
                    '-out',     out_file]

    if eblif_format:
        #Extended BLIF
        vqm2blif_cmd += ['-eblif_format']

    #Add any extra command line options
    if args.vqm2blif_extra_opts:
        vqm2blif_cmd = vqm2blif_cmd + args.vqm2blif_extra_opts.split()
    
    call_cmd("\nINFO: Calling vqm2blif", "ERROR: VQM to BLIF conversion failed", vqm2blif_cmd)
    
    pop_timer("Converting VQM to BLIF")


def run_fit(args):
    """
    Runs quartus fit on the specific project
    """
    push_timer("Running Quartus Fit")

    #Absolute path to vqm file, so it ends up in the script run directory
    args.vqm_file = path.join(os.getcwd(), args.vqm_file)

    #Quartus Verilog to VQM conversion script
    q2_flow_tcl = path.join(args.titan_dir, 'scripts/q2_flow.tcl')

    q2_shell = path.join(args.quartus_dir, 'quartus_sh')
    q2_cmd = [q2_shell,
                '--64bit',
                '-t',               q2_flow_tcl,
                '-project',         args.quartus_project,
                '-family',          args.device_family,
                '-report_dir',      args.report_dir,
                '-fit']

    if args.gen_post_fit_netlist:
        q2_cmd += ['-vqm_post_fit_out_file', args.vqm_post_fit_file]

    if args.run_fast_fit:
        q2_cmd += ['-fit_assignment_vars', "FITTER_EFFORT=FAST FIT"]

    print "Quartus CMD:" + " ".join(q2_cmd)
    #Quartus fit
    call_cmd("\nINFO: Calling Quartus", "ERROR: Quartus Fit failed", q2_cmd)
    
    pop_timer("Running Quartus Fit")

def run_sta(args, after_map=False):
    """
    Runs quartus sta on the specific project
    """
    push_timer("Running Quartus STA")

    #Absolute path to vqm file, so it ends up in the script run directory
    args.vqm_file = path.join(os.getcwd(), args.vqm_file)

    #Quartus Verilog to VQM conversion script
    q2_flow_tcl = path.join(args.titan_dir, 'scripts/q2_flow.tcl')

    #Specifies the reporting script to use
    sta_report_script = path.join(args.titan_dir, 'scripts/q2_sta_report.tcl')

    q2_shell = path.join(args.quartus_dir, 'quartus_sh')
    q2_cmd = [q2_shell,
                '--64bit',
                '-t',               q2_flow_tcl,
                '-project',         args.quartus_project,
                '-family',          args.device_family,
                '-report_dir',      args.report_dir]

    if after_map:
        q2_cmd += [ '-sta_map']
    else:
        q2_cmd += [ '-sta_fit']

    q2_cmd += [ '-sta_report_script', sta_report_script]

    #Quartus fit
    call_cmd("\nINFO: Calling Quartus", "ERROR: Quartus STA failed", q2_cmd)
    
    pop_timer("Running Quartus STA")

def run_vpr(args):
    """
    Runs vpr on the generated blif file
    """

    push_timer("Running VPR")
    vpr_exec = path.join(args.vpr_dir, 'vpr')

    vpr_cmd = [vpr_exec,
               args.arch_file,
               path.splitext(args.blif_file)[0]]
    
    if args.vpr_opts:
        vpr_cmd = vpr_cmd + args.vpr_opts.split()

    call_cmd("\nINFO: Calling VPR", "ERROR: VPR run failed", vpr_cmd)

    print "\nINFO: VPR ran successfully"
    pop_timer("Running VPR")


def call_cmd(info_text, error_text, cmd_array):
    try:
        print info_text
        print_cmd(cmd_array)
        sys.stdout.flush() #Ensure script output is in the correct order

        check_call_catch_exists(cmd_array)
    except subprocess.CalledProcessError as error:
        print "%s (retcode: %s)" % (error_text, error.returncode)
        sys.exit(1)

def print_cmd(cmd_array):
    print ' '.join(cmd_array)

def check_call_catch_exists(cmd_array):
    if os.path.isfile(cmd_array[0]):
        subprocess.check_call(cmd_array)
    else:
        print "ERROR: Could not find '%s'" % cmd_array[0]
        sys.exit(1)


def push_timer(timer_text):
    global g_timer_stack
    info_tuple = (timer_text, time())
    g_timer_stack.append(info_tuple)
    print "INFO: Started '{timer_text}'".format(timer_text=timer_text)

def pop_timer(timer_text):
    global g_timer_stack

    time_now = time()

    info_tuple = g_timer_stack.pop()
    if info_tuple[0] != timer_text:
        print "Error: Unbalanced Timers, timer_text '%s' and '%s' does not match" % (info_tuple[0],timer_text)
        sys.exit(1)

    elapsed_time = time_now - info_tuple[1]
    print "INFO: Ended   '{timer_text}' after {elapsed_time:.2f} sec".format(timer_text=timer_text, elapsed_time=elapsed_time)




#Execution starts here
if __name__ == '__main__':
    main()
