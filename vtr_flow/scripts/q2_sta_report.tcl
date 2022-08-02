#
# Simple QII STA reporting script
#
# Generates timing reports for all clock domains
# and can also writes out SDCs
#

#Reporting parameters
set npaths 1
set analysis_type setup

set report_dir [get_global_assignment -name PROJECT_OUTPUT_DIRECTORY]

#SDC writting parameters
set write_sdc_unexpanded 1
set unexpanded_sdc_file [file join $report_dir "unexpanded.sdc"]
set write_sdc_expanded 1
set expanded_sdc_file [file join $report_dir "expanded.sdc"]


puts "Generating QII Timing Reports"

# Report the worst paths in the design
puts "Generating QII Timing Report for $npaths worst paths in design"
report_timing -$analysis_type -npaths $npaths -detail path_only -show_routing -file [file join $report_dir "report_timing.rpt"]

# Report the worst paths per clock
set setup_domain_list [get_clock_domain_info -$analysis_type]
foreach domain $setup_domain_list {	
    set clk_name [lindex $domain 0]
    puts "Generating QII Timing Report for $npaths worst paths in domain $clk_name"
    report_timing -$analysis_type -npaths $npaths -detail path_only -show_routing -to_clock [lindex $domain 0] -from_clock [lindex $domain 0] -file [file join $report_dir "report_timing.$clk_name.rpt"]
}

if {$write_sdc_unexpanded} {
    puts "Writing Unexpanded SDC to file $unexpanded_sdc_file"
    write_sdc $unexpanded_sdc_file
}

if {$write_sdc_expanded} {
    puts "Writing Expanded SDC to file $expanded_sdc_file"
    write_sdc -expand $expanded_sdc_file
}

#What clock transfers were analyzed or cut
# Used to verify 'set_clock_groups -exclusive' worked correctly
report_clock_transfers -file [file join $report_dir "report_clock_transfers.rpt"]

#Report on any issues encountered when handling the SDC file(s)
report_sdc -file [file join $report_dir "report_sdc.rpt"]
#Ignored give more detail on any ignored sdc commands
report_sdc -ignored -file [file join $report_dir "report_sdc.ignored.rpt"]

#Report any unconstrained paths
report_ucp -file [file join $report_dir "report_ucp.rpt"]
