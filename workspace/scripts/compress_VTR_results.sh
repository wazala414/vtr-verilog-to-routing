# Compresses runXXX folders

cd $VTR_ROOT/workspace/benchmarking

echo -e "\nCompressing will delete all old zip archives named 'runXXX'."
echo -e '\nCompress (c) or decompress (d): '
read op

if [ "$op" == "c" ]; then
	find . -name "run*.z*" -delete
	find . -name "run*" -type d -execdir zip -s 90m -r {}.zip {} \;
	echo -e "\nCompression finished"
elif [ "$op" == "d" ]; then	
	find . -name "run*.zip" -exec 7z x {} \;
	echo -e "Decompression finished"
else
	echo -e "\nNo operation was executed"
fi
