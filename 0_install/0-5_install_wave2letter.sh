export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/
cd package
git clone https://github.com/kpu/kenlm.git
cd kenlm
mkdir -p build && cd build
cmake ..
make -j 4
cd ../../

kenlm=$(pwd)
export KENLM_ROOT_DIR=$kenlm/kenlm
export USE_CUDA=OFF
export USE_KENLM=ON
git clone -b v0.2 https://github.com/facebookresearch/wav2letter.git
cd wav2letter/bindings/python
pip install -e .