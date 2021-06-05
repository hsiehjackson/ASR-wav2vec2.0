rootdir=1_dataset/finetune
python $rootdir/0_transcribe.py
python $rootdir/1_genDictltr.py --transcript_file=1_dataset/finetune/training_dataset/transcript.txt --save_dir=1_dataset/finetune/training_dataset/
python $rootdir/2_manifest.py
python $rootdir/3_manifest_split.py