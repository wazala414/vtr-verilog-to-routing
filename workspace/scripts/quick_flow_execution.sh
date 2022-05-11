circuit=blink
arch=Same_Side_Preset
width=20

cd $VTR_ROOT/workspace/Test_Folder

$VTR_ROOT/vtr_flow/scripts/run_vtr_flow.py     $VTR_ROOT/workspace/circuits/$circuit.v     $VTR_ROOT/workspace/architectures/$arch.xml     -temp_dir .     --route_chan_width $width

cd $VTR_ROOT/workspace/Test_Folder

$VTR_ROOT/vpr/vpr	$VTR_ROOT/workspace/Test_Folder/$arch.xml	$VTR_ROOT/workspace/Test_Folder/$circuit.pre-vpr.blif	--route_chan_width $width --disp on