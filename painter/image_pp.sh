#! /bin/bash
source activate image_pp
python image_preprocessor.py --image=\'$1\' --grey=\'$2\' --xml=\'$3\'
source deactivate
