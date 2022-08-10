#!/bin/bash

### Script for aslprep singularity container
# Dylan Lawless
# Usage: run_aslprep: [--indir] [--outdir] [--m0scan] [--aslscan] [--aslsource] [--examcard] [--fs_license]


# Initialize defaults
export indir=NO_INDIR
export outdir=NO_OUTDIR
export level=participant
export m0scan=NO_M0SCAN
export aslscan=NO_ASLSCAN
export aslsource=NO_ASLSOURCE
export examcard=NO_EXAMCARD

# Parse options
while [[ $# -gt 0 ]]; do
  key="${1}"
  case $key in
    --indir)
      export indir="${2}"; shift; shift ;;
    --outdir)
      export outdir="${2}"; shift; shift ;;
    --m0scan)
      export m0scan="${2}"; shift; shift ;;
    --aslscan)
      export aslscan="${2}"; shift; shift ;;
    --sourcescan)
      export sourcescan="${2}"; shift; shift ;;
    --examcard)
      export examcard="${2}"; shift; shift ;;
    --fs_license)
      export fs_license="${2}"; shift; shift ;;
    *)
      echo Unknown input "${1}"; shift ;;
  esac
done


# Format BIDS directory and convert to nii
# Save Series Description to json
/opt/xnatwrapper/organize_data.py -i ${indir} -a ${aslscan} -m ${m0scan} -s ${sourcescan}

# Set BIDS directory
bidsdir=$indir/BIDS

#Get necessary data form examcard and write to json sidecar
/opt/xnatwrapper/examcard2json.py -i ${indir} -b ${bidsdir} -e ${examcard}

#Create ASL context tsv file
/opt/xnatwrapper/create_tsv.py -b ${bidsdir}

#Run aslprep
aslprep --fs-license-file ${fs_license} ${bidsdir} ${outdir} ${level} -w ${outdir}

#Run py scripts to convert outputs
/opt/xnatwrapper/html2pdf.py -o ${outdir}