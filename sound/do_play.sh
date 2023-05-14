#!/bin/bash

sndfile="$1"
shift
# valid languages: en-US, en-GB, de-DE, es-ES, fr-FR, it-IT
talk_lang="$1"
shift
talk_words=""
do_talk=0
while [ $# -gt 0 ]
do
    do_talk=1
    talk_words="$1 "
    shift
done

#no words - no talk!
if [ "$talk_words" == " " ]
then
    do_talk=0
    talk_words=""
fi

aplay -q $sndfile

if [ $do_talk -ne 0 ]
    then
    cd $(dirname $0)
    pico2wave -l $talk_lang -w stdout.wav "$talk_words" | aplay -q --
fi

exit 0
