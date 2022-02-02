#!/bin/bash

# Singularity
singularity run \
--cleanenv \
--contain \
--home $(pwd -P) \
--bind $(pwd -P)/EmotionBrain_BIDS:/data:ro \
--bind $(pwd -P)/OUTPUTS:/out:rw \
--bind $(pwd -P)/license.txt:/license/license.txt \
--bind $(pwd -P)/work:/work \
aslprep-0.2.7.simg \
--bidsdir $(pwd -P)/EmotionBrain_BIDS \
--outdir $(pwd -P)/OUTPUTS \
--m0scan pCASL_M0
--aslscan pCASL
--examcard $(pwd -P)/EmotionBrain_BIDS/Kaczkurkin_20210201.txt
--fs-license /license/license.txt \
-w $(pwd -P)/work

# Docker
docker run -ti -m 12GB --rm \
-v $(pwd -P)/EmotionBrain_BIDS:/data:ro \
-v $(pwd -P)/OUTPUTS:/out:rw \
-v $(pwd -P)/license.txt:/license/license.txt \
lawlessrd/aslprep:0.2.7 \
--bidsdir $(pwd -P)/EmotionBrain_BIDS \
--outdir $(pwd -P)/OUTPUTS \
--m0scan pCASL_M0 \
--aslscan pCASL \
--examcard $(pwd -P)/EmotionBrain_BIDS/Kaczkurkin_20210201.txt \
--fs-license /license/license.txt 
