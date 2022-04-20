#!/bin/bash

# Singularity
singularity run \
--cleanenv \
--contain \
--home $(pwd -P) \
--bind $(pwd -P)/INPUTS:/data:ro \
--bind $(pwd -P)/OUTPUTS:/out:rw \
--bind $(pwd -P)/license.txt:/license/license.txt \
aslprep.simg \
--indir $(pwd -P)/LANDMAN_UPGRAD \
--outdir $(pwd -P)/OUTPUTS \
--m0scan $(pwd -P)/INPUTS/pCASL_M0.dcm \
--aslscan $(pwd -P)/INPUTS/pCASL.dcm \
--sourcescan $(pwd -P)/INPUTS/source_pCASL.dcm \
--examcard $(pwd -P)/INPUTS/examcard.txt \
--fs_license $(pwd -P)/license.txt 