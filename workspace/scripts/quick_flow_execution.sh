circuit=blink
arch=Bidir_Arch_Test
#arch=Reference_Arch
width=20

#$VTR_ROOT/workspace/scripts/switchbox_architecture/full_switchblock_gen.py --same_side --chan_width=$width --in_arch=/home/vm/VTR-Tools/workspace/architectures/$arch.xml

cd $VTR_ROOT/workspace/Test_Folder

$VTR_ROOT/vtr_flow/scripts/run_vtr_flow.py     $VTR_ROOT/workspace/circuits/$circuit.v     $VTR_ROOT/workspace/architectures/$arch.xml     -temp_dir .     --route_chan_width $width

$VTR_ROOT/vpr/vpr     $VTR_ROOT/workspace/Test_Folder/$arch.xml     $circuit --circuit_file $circuit.pre-vpr.blif    --route_chan_width $width  --disp on #--analysis

#$VTR_ROOT/vpr/vpr	$VTR_ROOT/workspace/Test_Folder/$arch.xml	$VTR_ROOT/workspace/Test_Folder/$circuit.pre-vpr.blif	--route_chan_width $width --disp on --analysis