echo REDO_SOURCE_DIR=$REDO_SOURCE_DIR >&2
echo REDO_TARGET_DIR=$REDO_TARGET_DIR >&2

redo-ifchange b sub/c sub/d e
echo $$ >$3
