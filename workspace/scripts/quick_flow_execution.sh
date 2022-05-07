circuit=blink
arch=Reference_Arch
width=50

cd
cd $VTR_ROOT/workspace/Test_Folder

$VTR_ROOT/vtr_flow/scripts/run_vtr_flow.py     $VTR_ROOT/workspace/Basic_Architecture/$circuit.v     $VTR_ROOT/workspace/Basic_Architecture/$arch.xml     -temp_dir .     --route_chan_width $width --echo_file on --write_rr_graph rr_graph_echo.xml

cd
cd $VTR_ROOT/workspace/scripts/switchbox_architecture
./same_side_locator.py -panda -edit

cd
cd $VTR_ROOT/workspace/Test_Folder

#$VTR_ROOT/vpr/vpr	$VTR_ROOT/workspace/Test_Folder/$arch.xml	$VTR_ROOT/workspace/Test_Folder/$circuit.pre-vpr.blif	--route_chan_width $width --read_rr_graph rr_graph2.xml --disp on
