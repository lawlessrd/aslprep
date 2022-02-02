#!/bin/bash

# Singularity
singularity run \
--cleanenv \
--contain \
--home $(pwd -P) \
--bind $(pwd -P)/EmotionBrain_BIDS:/data:ro \
--bind $(pwd -P)/OUTPUTS:/out:rw \
--bind $(pwd -P)/license.txt:/license/license.txt \
aslprep_v1.simg \
--bidsdir $(pwd -P)/EmotionBrain_BIDS \
--outdir $(pwd -P)/OUTPUTS \
--m0scan pCASL_M0 \
--aslscan pCASL \
--examcard $(pwd -P)/EmotionBrain_BIDS/Kaczkurkin_20210201.txt \
--fs_license $(pwd -P)/EmotionBrain_BIDS/license.txt

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
--fs_license $(pwd -P)/license.txt 

