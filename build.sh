
clear 
log_file="./build.log"

cmd="-b"
if [[ $1 == "r" || $1 == "rebuild" ]]
then 
    cmd="-r"
fi 

UV4.exe $cmd ./*.uvprojx -j0 -o $log_file 

echo "build log >>"
cat $log_file

rm $log_file