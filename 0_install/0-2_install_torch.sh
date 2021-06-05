OUTPUT=$(nvcc --version)
VERSION="$(cut -d',' -f2 <<<$OUTPUT)"
VERSION="$(cut -d' ' -f2 <<<$OUTPUT)"

if [[ VERSION == "10.0" ]]
then
  VERSION_SUFFIX="+cu100"
elif [[ VERSION == "10.1" ]]
then
  VERSION_SUFFIX="+cu101"
elif [[ VERSION == "10.2" ]]
then
  VERSION_SUFFIX="+cu102"  
else
  VERSION_SUFFIX="+cu110"
fi

echo $VERSION_SUFFIX
pip install torch==1.7.1$VERSION_SUFFIX -f https://download.pytorch.org/whl/torch_stable.html


