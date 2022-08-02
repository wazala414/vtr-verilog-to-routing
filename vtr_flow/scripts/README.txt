This folder contains scripts for running the Titan Flow.

These scripts have been tested under Ubuntu 12.04 64-bit
using Quartus 12.0 (no service packs).

Directory Structure
--------------------------------------------------
    titan_flow.py:
        High level script to run the Titan flow, that acts as a wrapper around 
        q2_flow.tcl and vqm2blif.exe. It generates a VQM and BLIF file from a 
        Quartus II project. It can also optionally run quartus_fit and/or vpr 
        after VQM and BLIF generation.

        For example, to generate a blif file for the 'radar20' benchmark using
        the simple Stratix IV architecture:
            $TITAN_BASE_DIR/scripts/titan_flow.py -q $TITAN_BASE_DIR/benchmarks/other_benchmarks/radar20/quartus2_proj/radar20.qpf -a $TITAN_BASE_DIR/arch/stratixiv_arch.timing.xml
        
        See 'titan_flow.py -h' for detailed options.


    q2_flow.tcl:
        Low level script for Quartus II, used to synthesize a project and 
        optionally dump a VQM, and/or fit the design.  It must be run by the 
        quartus_sh executable.

        For example, to generate a vqm file for the 'radar20' benchmark 
        targeting the Stratix IV family:
            quartus_sh -t $TITAN_BASE_DIR/scripts/q2_flow.tcl -project $TITAN_BASE_DIR/benchmarks/other_benchmarks/radar20/quartus2_proj/radar20.qpf -family stratixiv -synth -vqm_out_file radar20_stratixiv.vqm

        See 'quartus_sh -t $TITAN_BASE_DIR/scripts/q2_flow.tcl -h' for detailed options.

    q2_sta_report.tcl:
        Script used for Quartus II timing analysis. Writes out timing reports, and
        SDC files.  Can be used with q2_flow.tcl's -sta_report_script option.

    create_release.py:
        Used to generate a release of the Titan Flow from its source tree.
        See 'create_release.py -h' for detailed options.
