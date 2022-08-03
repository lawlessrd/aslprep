#!/bin/bash

# Singularity
singularity run \
--cleanenv \
--contain \
--home $(pwd -P) \
--bind $(pwd -P)/INPUTS:/data:ro \
--bind $(pwd -P)/OUTPUTS:/out:rw \
--bind $(pwd -P)/license.txt:/license/license.txt \
--bind $(pwd -P)/work:/work:rw \
aslprep.simg \
--indir $(pwd -P)/INPUTS \
--outdir $(pwd -P)/OUTPUTS \
--m0scan $(pwd -P)/INPUTS/ASL_M0.dcm \
--aslscan $(pwd -P)/INPUTS/ASL.dcm \
--sourcescan $(pwd -P)/INPUTS/ASL_source.dcm \
--examcard $(pwd -P)/INPUTS/examcard.txt \
--fs_license $(pwd -P)/license.txt 