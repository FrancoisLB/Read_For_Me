#/bin/bash
# Usage :
# ./tests.sh >tests.log &>/dev/null

for file in input/*.jpg
do
    if [[ -f $file ]]; then
        name=`basename $file .jpg`
        python3 ../textreader.py --basename input/$name --time
    fi
done

