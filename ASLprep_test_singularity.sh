#!/bin/bash

# Singularity
singularity run \
--cleanenv \
--contain \
--home $(pwd -P) \
--bind $(pwd -P)/LANDMAN_UPGRAD:/data:ro \
--bind $(pwd -P)/OUTPUTS:/out:rw \
--bind $(pwd -P)/license.txt:/license/license.txt \
aslprep.simg \
--bidsdir $(pwd -P)/LANDMAN_UPGRAD \
--outdir $(pwd -P)/OUTPUTS \
--m0scan 'ASL_M0 Ref' \
--aslscan 'ASL_BASELINE PGPP' \
--examcard $(pwd -P)/Landman_EC.txt \
--fs_license $(pwd -P)/license.txt \
--project 'test_project' \
--subject 'test_subject' \
--session 'test_session'