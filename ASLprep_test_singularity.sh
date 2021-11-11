#!/bin/bash

singularity run \
--cleanenv \
--contain \
--home $(pwd -P) \
--bind $(pwd -P)/EmotionBrain_BIDS:/data:ro \
--bind $(pwd -P)/OUTPUTS:/out:rw \
--bind $(pwd -P)/license.txt:/license/license.txt \
--bind $(pwd -P)/work:/work \
aslprep-0.2.7.simg \
$(pwd -P)/EmotionBrain_BIDS \
$(pwd -P)/OUTPUTS \
participant \
--participant-label 01 \
--fs-license-file /license/license.txt \
-w $(pwd -P)/work