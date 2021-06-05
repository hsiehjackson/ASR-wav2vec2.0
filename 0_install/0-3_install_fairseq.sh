mkdir package
cd package/
git clone https://github.com/pytorch/fairseq.git
cd fairseq
git checkout b8786dc2aadb56bb549f92ed542875096868bdd5
pip install --editable ./