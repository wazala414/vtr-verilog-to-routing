circuit=ch_intrinsics_modified
#arch=full_arch_benchmarking/Unidir/Unidir_Full_Same_Side/arch/Unidir_Basic_Full_Same_Side
arch=/home/vm/VTR-Tools/vtr_flow/arch/same_side/ultrascale_ispd/Reference.xml
#arch=test
width=150


#$VTR_ROOT/workspace/scripts/switchbox_architecture/full_switchblock_gen.py --same_side --chan_width=$width --in_arch=/home/vm/VTR-Tools/workspace/architectures/$arch.xml

cd $VTR_ROOT/workspace/Test_Folder

$VTR_ROOT/vtr_flow/scripts/run_vtr_flow.py     $VTR_ROOT/vtr_flow/benchmarks/hdl_include/$circuit.v     $arch     -temp_dir .     --route_chan_width $width

$VTR_ROOT/vpr/vpr     $arch     $circuit --circuit_file $circuit.pre-vpr.blif    --route_chan_width $width  --disp on --analysis #--analysis

# #$VTR_ROOT/vpr/vpr	$VTR_ROOT/workspace/Test_Folder/$arch.xml	$VTR_ROOT/workspace/Test_Folder/$circuit.pre-vpr.blif	--route_chan_width $width --disp on --timing_analysis off # --analysis


# $VTR_ROOT/vtr_flow/scripts/run_vtr_task.py     $VTR_ROOT/workspace/circuits/$circuit.v     $VTR_ROOT/workspace/architectures/$arch.xml     -temp_dir .     --route_chan_width $width --timing_analysis off


$VTR_ROOT/vtr_flow/scripts/run_vtr_flow.py     $VTR_ROOT/workspace/circuits/ZeroAMP_circuit/empty_circuit.v     $VTR_ROOT/workspace/architectures/ZeroAMP_arch/Fully_Connected_SB.xml     -temp_dir .     --route_chan_width 4

$VTR_ROOT/vpr/vpr     $VTR_ROOT/workspace/architectures/ZeroAMP_arch/Fully_Connected_SB.xml     empty_circuit --circuit_file empty_circuit.odin.blif    --route_chan_width 4  --disp on