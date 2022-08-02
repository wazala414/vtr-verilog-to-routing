#!/usr/bin/python
__version__ = "create_release.py"

#Debugger
try:
    import pudb
except ImportError:
    pass

import sys
import argparse
import subprocess
import os
import errno
import fnmatch
import shutil
import multiprocessing
import re
from os import path
from time import time
import fileinput

BENCHMARK_DIRS = ['benchmarks/titan23', 'benchmarks/other_benchmarks']
Q2_PROJECT_DIR = 'quartus2_proj'

BENCHMARKS_TO_NOT_RELEASE_SOURCE = ['minres']
SOURCE_HDL_DIRECTORIES = ['orig', 'quartus2_proj']

#Some benchmarks use a large amount of memory to synthesize,
# list them here so we don't run too many of them in parallel
large_benchmark_synth_mem_GB = {'gaussianblur': 18,
                                'bitcoin_miner': 8,
                                'directrf': 9,
                                'sparcT1_chip2': 23,
                                'LU_Network': 6,
                                'LU230': 6,
                                'mes_noc': 6,
                                'gsm_switch': 5,
                                'denoise': 4,
                                'sparcT2_core': 5, }
def main():
    """
    The main function
    """
    #Print the command line
    for arg in sys.argv:
        print arg,
    print

    #Argument parsing
    args = parse_args()

    print "Generating TITAN release"

    create_release(args)

    print
    print "End of script %s" % sys.argv[0]

def parse_args():
    description="""\
    Generates a release of the Titan Flow & Benchmarks

    Copies the Titan source directory tree, and then uses Quartus 
    to generate VQMs for each benchmark.  Also copies the VQM2BLIF
    source tree and compiles it.  The compiled vqm2blif is then
    used to convert the VQMs to BLIFs.  Finally the release tree
    is cleaned up.
    """

    parser = argparse.ArgumentParser(usage="%(prog)s [-h] -t TITAN_SRC_DIR -v vqm2blif_src_dir -a ARCH_FILE -o OUTPUT_DIR [other options]",
                                    description=description)
    parser.add_argument('--version', action='version', version=__version__,
                        help='Version information')

    input_options = parser.add_argument_group('input_options')
    
    input_options.add_argument('-t', '--titan_src_dir', dest='titan_src_dir', action='store',
                        required=True,
                        help="The titan source directory")
    
    input_options.add_argument('-v', '--vqm2blif_src_dir', dest='vqm2blif_src_dir', action='store',
                       required=True,
                       help="The directory containing VQM2BLIF's source tree")

    input_options.add_argument("-q", "--quartus_bin_dir", dest="quartus_bin_dir", action='store',
                       required=True,
                       help="The directory containing the Quartus binaries (e.g. quartus_sh)")

    input_options.add_argument("--vpr_bin_dir", dest="vpr_bin_dir", action='store',
                       required=True,
                       help="The directory containing the VPR binary (e.g. vpr)")
    
    input_options.add_argument('-a', '--arch_file', dest='arch_file', action='store',
                       required=True,
                       help="The arch_file to use for BLIF generation")
    

    output_options = parser.add_argument_group('output_options')

    output_options.add_argument('-o', '--output_dir', dest='output_dir', action='store',
                       required=True,
                       help="Directory to build release in, will be removed if it exists")
    output_options.add_argument('--safe_arch_name', dest='safe_arch_name', action='store',
                       default=None,
                       required=False,
                       help="Safe architecture name to append to netlist files. Will be automatically defined if not provided.")


    script_options = parser.add_argument_group('script_options')
    
    script_options.add_argument('--clean_only', dest='clean_only', action='store_true',
                       default=False,
                       help="Only run the cleaning step")

    script_options.add_argument('-n', '--ncpu', dest='num_cpus', action='store',
                       type=int, default=1,
                       help="Number of CPUs to use while generating release (default: %(default)s)")

    script_options.add_argument('--machine_memory_GB', dest='machine_memory_GB', action='store',
                       default=16.0, type=float,
                       help="Amount of memory available on this machine in GB. Used to avoid running too many jobs in parallel (default: %(default)s)")

    script_options.add_argument('--sdc_clock_block_pct_threshold',
                        default=0.1, type=float,
                        help="The minimum fanout threshold (as a percentage of design primitives) for a netlist clock to be included in the generated SDC files. This ensures that small clocks don't skew the QoR comparision between VPR and Quartus (default: %(default)s)")


    #Actually evaluate the arguments
    args = parser.parse_args()

    if not args.safe_arch_name:
        safe_arch_name = os.path.basename(args.arch_file)
        safe_arch_name = os.path.splitext(safe_arch_name)[0]
        args.safe_arch_name = safe_arch_name.replace('.', '_') #Q2 errors if there is more than one '.' in the vqm filename

    return args

def create_release(args):

    if not args.clean_only:
        if os.path.isdir(args.output_dir):
            print "Removing existing output directory"
            shutil.rmtree(args.output_dir)

        release_titan_tree(args)

        vqm2blif_dir = release_vqm2blif(args)

        #Generate a list of benchmark qpf files
        qpf_list = find_qpf_files(args.output_dir)

        print

        generate_vqm_and_blif(args, vqm2blif_dir, qpf_list)

        update_readme_files(args)

    cleanup_release(args)

def release_titan_tree(args):
    print "Copying release tree"
    shutil.copytree(args.titan_src_dir, args.output_dir)



def release_vqm2blif(args):
    print "Copying VQM2BLIF files"
    VQM2BLIF_DIRS_FILES_TO_COPY = ['cmake', 'CMakeLists.txt', 'DOCS', 'libs', 'Makefile', 'REG_TEST', 'src', 'README.txt']
    vqm2blif_release_dir = os.path.join(args.output_dir, 'vqm_to_blif')

    for dir_files in VQM2BLIF_DIRS_FILES_TO_COPY:
        src_dir = os.path.join(args.vqm2blif_src_dir, dir_files)
        dst_dir = os.path.join(vqm2blif_release_dir, dir_files)
        if os.path.isdir(src_dir):
            shutil.copytree(src_dir, dst_dir)
        else:
            shutil.copyfile(src_dir, dst_dir)

    #Compile VQM2BLIF
    pwd = os.getcwd()

    os.chdir(vqm2blif_release_dir)

    print "Compiling VQM2BLIF"
    subprocess.call('make clean', shell=True)

    cmd = ['make',
           '-j', str(args.num_cpus)]
    subprocess.call(cmd)

    os.chdir(pwd)

    #Check that the executable was generated
    vqm2blif_exec = os.path.join(vqm2blif_release_dir, 'vqm2blif')
    if not os.path.isfile(vqm2blif_exec) or not os.path.getsize(vqm2blif_exec) > 0:
        print "Error: vqm2blif invalid or not created!"
        sys.exit(1)


    return vqm2blif_release_dir


def find_qpf_files(base_dir):
    qpf_file_paths = []
    for benchmark_dir in BENCHMARK_DIRS:
        benchmark_dir_path = os.path.join(base_dir, benchmark_dir)
        #Get the directories in the parent directory
        # walk recursively walks the tree, calling next()
        # generates the list of the current directory
        # which is a tuple of (dirpath, dirnames, filenames)
        # we get the dirnames by grabbing the list at index 1
        for benchmark in os.walk(benchmark_dir_path).next()[1]:
            #Skip the .svn directory
            if benchmark == '.svn':
                continue

            benchmark_path = os.path.join(benchmark_dir_path, benchmark, Q2_PROJECT_DIR)

            qpf_files = fnmatch.filter(os.walk(benchmark_path).next()[2], '*qpf')
            assert(len(qpf_files) == 1)
            qpf_file = qpf_files[0]

            qpf_file_path = os.path.join(benchmark_path, qpf_file)
            qpf_file_paths.append(qpf_file_path)

    #qpf_file_paths = [x for x in qpf_file_paths if 'neuron' in x]
    #print qpf_file_paths

    return qpf_file_paths

def generate_vqm_and_blif(args, vqm2blif_dir, benchmark_qpfs):

    benchmarks_by_ncpus = split_qpfs_by_synth_memory(args, benchmark_qpfs)


    for cpu_cnt in reversed(xrange(1, args.num_cpus+1)):
        if cpu_cnt in benchmarks_by_ncpus:
            benchmark_qpfs = benchmarks_by_ncpus[cpu_cnt]

            print "Creating pool of %d processes to generate netlists in parallel" % cpu_cnt
            pool = multiprocessing.Pool(cpu_cnt)

            try:
                results = []
                for cnt, qpf in enumerate(benchmark_qpfs):
                    #res = pool.apply_async(test, (args, qpf))

                    res = pool.apply_async(gen_vqm_blif_worker, (args, vqm2blif_dir, qpf))
                    results.append(res)

                    #gen_vqm_blif_worker(args, vqm2blif_dir, qpf)


                pool.close() #No more jobs
                pool.join() #Wait to finish

                for res in results:
                    if res.get() != True:
                        raise RuntimeError("Failed to process benchmark")
            except KeyboardInterrupt:
                print "Parent Process recieved keyboard interrupt, terminating all processies"
                pool.terminate()
                pool.join()

            print 

    print "Finished VQM and BLIF generation"


def split_qpfs_by_synth_memory(args, benchmark_qpfs):
    benchmarks_by_ncpus = {}

    for cpu_cnt in xrange(1, args.num_cpus+1):
        benchmarks_by_ncpus[cpu_cnt] = []


    for benchmark_qpf in benchmark_qpfs:
        benchmark_name = os.path.basename(os.path.dirname(os.path.dirname(benchmark_qpf)))


        if benchmark_name in large_benchmark_synth_mem_GB:
            benchmark_synth_memory = large_benchmark_synth_mem_GB[benchmark_name]
            added_benchmark = False

            #Try to find the most parrallel list that will support the memory requirement
            for cpu_cnt in reversed(xrange(1, args.num_cpus+1)):
                mem_per_process = float(args.machine_memory_GB) / cpu_cnt
                if mem_per_process > benchmark_synth_memory:
                    added_benchmark = True
                    benchmarks_by_ncpus[cpu_cnt].append(benchmark_qpf)
                    break

            #If it didn't fit, just put it in the serial list
            if not added_benchmark:
                print "Warning: benchmark '%s' may use > %d GB of memory to synthesize, which may cause paging to disk" % (benchmark_name, args.machine_memory_GB)
                benchmarks_by_ncpus[1].append(benchmark_qpf)

        else:
            #Unlisted are assumed to fit no matter what
            benchmarks_by_ncpus[args.num_cpus].append(benchmark_qpf)

    #Fix up
    for cpu_cnt in reversed(xrange(1, args.num_cpus+1)):
        #Merge with the next (smaller) number of cpus, if all cpus won't be utilized
        if len(benchmarks_by_ncpus[cpu_cnt]) < cpu_cnt and cpu_cnt > 1:
            benchmarks_by_ncpus[cpu_cnt-1] =   benchmarks_by_ncpus[cpu_cnt] +  benchmarks_by_ncpus[cpu_cnt-1]
            del benchmarks_by_ncpus[cpu_cnt]

    return benchmarks_by_ncpus

def test(args, qpf_file):
    print "Worker qpf: %s" %  qpf_file

    return

def gen_vqm_blif_worker(args, vqm2blif_dir, qpf_file):
    try:
        start_time = time()

        benchmark_dir = os.path.dirname(os.path.dirname(qpf_file))
        benchmark_name = os.path.basename(benchmark_dir)
        netlists_dir = os.path.join(benchmark_dir, 'netlists')

        mkdir_p(netlists_dir)

        titan_flow_script = os.path.join(args.titan_src_dir, 'scripts', 'titan_flow.py')

        local_arch_path = os.path.join(args.output_dir, 'arch', args.arch_file)

        blif_netlist_name = '_'.join([benchmark_name, args.safe_arch_name])

        vqm_netlist_name = '_'.join([benchmark_name, args.safe_arch_name.split('_')[0]]) #Extract just until the first underscore (e.g. stratixiv_arch_simple => stratixiv

        netlist_log = os.path.join(netlists_dir, 'netlist_gen.log')

        vqm_file_path = os.path.join(netlists_dir, '.'.join([vqm_netlist_name, 'vqm']))
        blif_file_path = os.path.join(netlists_dir, '.'.join([blif_netlist_name, 'blif']))
        eblif_file_path = os.path.join(netlists_dir, '.'.join([blif_netlist_name, 'eblif']))

        cmd = [titan_flow_script,
                '-q', qpf_file,
                '-a', local_arch_path,
                '-v', vqm_file_path,
                '-b', blif_file_path,
                '-e', eblif_file_path,
                '--titan_dir', args.output_dir,
                '--vqm2blif_dir', vqm2blif_dir,
                '--quartus_dir', args.quartus_bin_dir,
                #'--report_dir', '/dev/null', #Dont' write out any reports
                ]

        #print "Calling: ", ' '.join(cmd)
        print "Starting Netlist Generation for %s" % benchmark_name
        
        #Run the titan_flow script
        with open(netlist_log, 'w') as f:
            try:
                subprocess.check_call(cmd, stdout=f, stderr=f)
            except subprocess.CalledProcessError as e:
                print "Failed to generate netlist for {name} ({error}: exit code {code})".format(name=benchmark_name, error=str(e), code=e.returncode)
                return False

        #Verify that the blif and vqm were generated
        if not os.path.isfile(vqm_file_path):
            print "Error: Could not find generated vqm file: %s" % vqm_file_path
            return False
        if not os.path.getsize(vqm_file_path) > 0:
            print "Error: Generated vqm file '%' of size: %d" % (vqm_file_path, os.path.getsize(vqm_file_path))
            return False

        if not os.path.isfile(blif_file_path):
            print "Error: Could not find generated blif file: %s" % blif_file_path
            return False
        if not os.path.getsize(blif_file_path) > 0:
            print "Error: Generated blif file '%' of size: %d" % (blif_file_path, os.path.getsize(blif_file_path))
            return False

        #Generate compatible VPR & Q2 SDC Files
        # First, we run VPR (which reports the netlist clocks found) [This also verifies that VPR can load the generated BLIF]
        # Second, we generate both Quartus and VPR equivalent SDC files
        cmd = [os.path.join(args.vpr_bin_dir, "vpr"), local_arch_path, blif_file_path, "--pack", "--exit_before_pack", "on"]
        try:
            vpr_output = subprocess.check_output(cmd)
        except subprocess.CalledProcessError as e:
            print "Failed collect netlist clocks from VPR for {name} ({error}: exit code {code})".format(name=benchmark_name, error=str(e), code=e.returncode)
            return False

        generate_sdc_files(benchmark_dir, benchmark_name, vpr_output, args.sdc_clock_block_pct_threshold)

        print "Finished Netlist Generation for %s after %d sec" % (benchmark_name, time() - start_time)

    except KeyboardInterrupt:
        print "Worker recieved keybaord interupt"
        return False

    return True #Success

def generate_sdc_files(benchmark_dir, benchmark_name, vpr_output, netlist_clock_fanout_threshold):
    sdc_dir = os.path.join(benchmark_dir, "sdc")
    mkdir_p(sdc_dir)

    quartus_sdc = os.path.join(sdc_dir, "quartus.sdc")
    vpr_sdc = os.path.join(sdc_dir, "vpr.sdc")
    sdc_gen_log = os.path.join(sdc_dir, "sdc_gen.log")

    with open(sdc_gen_log, 'w') as f:
        print >>f, "Invoked VPR to detect clocks:"
        print >>f, "=============================="
        print >>f, vpr_output

        print >>f, ""
        print >>f, ""
        print >>f, "Detected the following clocks:"
        print >>f, "=============================="
        #Load up the names of all the VPR detected clocks
        NETLIST_CLOCK_REGEX = re.compile(r"\s*Netlist Clock '(?P<clock_name>\S+)' Fanout: (?P<pins>\S+) pins \((?P<pins_pct>\S+)%\), (?P<blocks>\S+) blocks \((?P<blocks_pct>\S+)%\)")
        vpr_clocks = []
        for line in vpr_output.split('\n'):

            match = NETLIST_CLOCK_REGEX.match(line)
            if match:
                clock = match.groupdict()['clock_name']
                pins = int(match.groupdict()['pins'])
                blocks = int(match.groupdict()['blocks'])
                pins_pct = float(match.groupdict()['pins_pct'])
                blocks_pct = float(match.groupdict()['blocks_pct'])


                if blocks_pct < netlist_clock_fanout_threshold:
                    print >>f, "Generate {} SDC: Skipping small clock {}: {} pins ({}%) {} blocks ({}%)".format(
                            benchmark_name,
                            clock,
                            pins, pins_pct,
                            blocks, blocks_pct)
                    continue
                print >>f, "Generate {} SDC: Creating clock {}: {} pins ({}%) {} blocks ({}%)".format(
                        benchmark_name,
                        clock,
                        pins, pins_pct,
                        blocks, blocks_pct)

                vpr_clocks.append(clock)
        generate_sdc(quartus_sdc, clocks=vpr_clocks, tool="quartus", benchmark_name=benchmark_name, period=1., uncertainty=0.0, netlist_clock_fanout_threshold=netlist_clock_fanout_threshold)
        generate_sdc(vpr_sdc, clocks=vpr_clocks, tool="vpr", benchmark_name=benchmark_name, period=1., uncertainty=0.0, netlist_clock_fanout_threshold=netlist_clock_fanout_threshold)

def generate_sdc(sdc_filepath, clocks, tool, benchmark_name, period, uncertainty, netlist_clock_fanout_threshold=None):
    assert tool in ['quartus', 'vpr']

    with open(sdc_filepath, 'w') as f:
        if tool == 'quartus':
            print >>f, "#Quartus compatible SDC file for benchmark circuit '{}'".format(benchmark_name)
        else:
            print >>f, "#VPR compatible SDC file for benchmark circuit '{}'".format(benchmark_name)
        print >>f, ""
        print >>f, "# Creates an external virtual clock 'virtual_io_clock', and non-virtual clocks for each netlist clock (each with 1ns target clock period)."
        print >>f, "# Paths between netlist clock domains are not analyzed, but paths to/from the 'virtual_io_clock' and netlist clocks are analyzed."
        if netlist_clock_fanout_threshold != None:
            print >>f, "# Small clocks which drive less than {}% of blocks are ignored and not created".format(netlist_clock_fanout_threshold)

        if tool == 'quartus':
            print >>f, ""
            print >>f, "#**************************************************************"
            print >>f, "# Reset Constraints"
            print >>f, "#**************************************************************"
            print >>f, "#Some benchmarks contain SDC statements embedded in HDL"
            print >>f, "#produced by Quartus (e.g. altera_reset_controller)."
            print >>f, "#"
            print >>f, "#Since we can't remove such SDC statements we reset"
            print >>f, "#the design which drops *all* constraints, and then apply"
            print >>f, "#our own constraints"
            print >>f, "reset_design"

        print >>f, ""
        print >>f, "#**************************************************************"
        print >>f, "# Unit Information"
        print >>f, "#**************************************************************"

        if tool == 'quartus':
            print >>f, "set_time_format -unit ns -decimal_places 3"
        else:
            print >>f, "#VPR assumes time unit is nanoseconds"

        print >>f, ""
        print >>f, "#**************************************************************"
        print >>f, "# Create Clock"
        print >>f, "#**************************************************************"
        print >>f, "create_clock -period {period:.3f} -name virtual_io_clock".format(period=period)
        for clock in clocks:
            if tool == "vpr":
                clock = escape_vpr_clock_name(clock)

            if tool == "quartus":
                #According to the Quartus documentation, get_keepers returns any matching non-combinational
                # top-level port (i.e. primary I/O), netlist pin (e.g. PLL output) or clock.
                #
                # This should be more robust than get_ports if the clock is defined in a netlist pin (e.g. PLL)
                print >>f, "create_clock -period {period:.3f} -name {{{clock}}} {{{clock}}}".format(period=period, clock=clock)
            else:
                #VPR expects the clock pattern match to be the clock net's name
                print >>f, "create_clock -period {period:.3f} {{{clock}}}".format(period=period, clock=clock)


        print >>f, ""
        print >>f, "#**************************************************************"
        print >>f, "# Create Generated Clock"
        print >>f, "#**************************************************************"
        print >>f, "#None"

        print >>f, ""
        print >>f, "#**************************************************************"
        print >>f, "# Set Clock Latency"
        print >>f, "#**************************************************************"
        for clock in clocks:
            if tool == "vpr":
                clock = escape_vpr_clock_name(clock)
            print >>f, "set_clock_latency -source 0.000 [get_clocks {{{clock}}}]".format(clock=clock)

        print >>f, ""
        print >>f, "#**************************************************************"
        print >>f, "# Set Clock Uncertainty"
        print >>f, "#**************************************************************"
        #Quartus requires the -to option, so we just enumerate all pairs
        for from_clk in clocks + ['virtual_io_clock']:
            if tool == "vpr":
                from_clk = escape_vpr_clock_name(from_clk)
            for to_clk in clocks + ['virtual_io_clock']:
                if tool == "vpr":
                    to_clk = escape_vpr_clock_name(to_clk)

                print >>f, "set_clock_uncertainty -from [get_clocks {{{from_clk}}}] -to [get_clocks {{{to_clk}}}] {uncertainty:.3f}".format(
                                        from_clk=from_clk,
                                        to_clk=to_clk,
                                        uncertainty=uncertainty)

        print >>f, ""
        print >>f, "#**************************************************************"
        print >>f, "# Set Input Delay"
        print >>f, "#**************************************************************"
        print >>f, "set_input_delay -clock virtual_io_clock 0.0 [get_ports *]"

        print >>f, ""
        print >>f, "#**************************************************************"
        print >>f, "# Set Output Delay"
        print >>f, "#**************************************************************"
        print >>f, "set_output_delay -clock virtual_io_clock 0.0 [get_ports *]"

        print >>f, ""
        print >>f, "#**************************************************************"
        print >>f, "# Set Clock Groups"
        print >>f, "#**************************************************************"
        if len(clocks) > 1:
            print >>f, "set_clock_groups -exclusive \\"
            for i, clock in enumerate(clocks):
                if tool == "vpr":
                    clock = escape_vpr_clock_name(clock)

                print >>f, "                 -group {{{clk}}}".format(clk=clock),
                
                if i != len(clocks) - 1:
                    print >>f, " \\"
                else:
                    print >>f, ""
        else:
            print >>f, "#None"

        print >>f, ""
        print >>f, "#**************************************************************"
        print >>f, "# Set False Path"
        print >>f, "#**************************************************************"
        print >>f, "#None"

        print >>f, ""
        print >>f, "#**************************************************************"
        print >>f, "# Set Multicycle Path"
        print >>f, "#**************************************************************"
        print >>f, "#None"

        print >>f, ""
        print >>f, "#**************************************************************"
        print >>f, "# Set Maximum Delay"
        print >>f, "#**************************************************************"
        print >>f, "#None"

        print >>f, ""
        print >>f, "#**************************************************************"
        print >>f, "# Set Minimum Delay"
        print >>f, "#**************************************************************"
        print >>f, "#None"

        print >>f, ""
        print >>f, "#EOF"

def escape_vpr_clock_name(clock_name):

    escaped_clock_name = clock_name
    for char_to_escape in ['\\', '|', '[', ']', '$', '^']: #Note: we do literal backslash first to avoid escaping the escapes
        escaped_clock_name = escaped_clock_name.replace(char_to_escape, '\\' + char_to_escape)

    return escaped_clock_name

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def cleanup_release(args):
    # Remove .svn and .git files
    # Remove vqm2blif (s), 'make clean'
    # Remove db and incremental_db, report_dirs (sent to /dev/null?)
    # Remove .git and .gitignore files
    # HDL files not to be released
    print "Cleaning Intermediate Files"

    os.chdir(args.output_dir)

    #File patterns to remove,
    clean_patterns = ['*svn*',
                      '*git*',
                      '*.git*',
                      'db',
                      'incremental_db',
                      '*.rpt',
                      '*.summary',
                      '*.smsg',
                      '*.done',
                      '*.pyc'
                      ]
    for pattern in clean_patterns:
        print "Recursively removing files matching '%s'" % pattern
        cmd = ['find',
               '-name', "".join(["'", pattern, "'"]),
               ' | ',
               'xargs rm -rf']
        cmd = ' '.join(cmd)
        subprocess.call(cmd, shell=True)

    print "Running 'make distclean' on vqm2blif"
    vqm2blif_release_dir = os.path.join('vqm_to_blif')
    pwd = os.getcwd()
    os.chdir(vqm2blif_release_dir)
    subprocess.call('make distclean', shell=True)
    os.chdir(pwd)


    #Remove benchmarks for which sources are not to be released
    for benchmark_dir in BENCHMARK_DIRS:
        for benchmark in BENCHMARKS_TO_NOT_RELEASE_SOURCE:
            potential_dir = os.path.join(benchmark_dir, benchmark)
            if os.path.isdir(potential_dir):
                #Remove the source for this benchmark

                for hdl_dir in SOURCE_HDL_DIRECTORIES: 
                    src_dir = os.path.join(potential_dir, hdl_dir)
                    print "Removing source HDL in '%s'" % src_dir
                    shutil.rmtree(src_dir)

def update_readme_files(args):
    #Find all the readme.txt files
    readme_files = []
    for(dirpath, dirs, files) in os.walk(args.output_dir):
        for filename in files:
            if filename == "README.txt":
                readme_files.append(os.path.join(dirpath, filename))

    #Perform text replacement as required
    for readme_file in readme_files:
        for line in fileinput.input(readme_file, inplace=True):
            print update_readme_line(args, line),

def update_readme_line(args, line):
    replace_dict = {'{ARCH_FILE_BASENAME}': os.path.basename(args.arch_file),
                    '{NETLIST_ARCH_SUFFIX}': args.safe_arch_name}


    new_line = line
    for key, value in replace_dict.iteritems():
        new_line = new_line.replace(key, value)

    return new_line

#Execution starts here
if __name__ == '__main__':
    main()
