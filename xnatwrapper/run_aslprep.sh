#!/bin/bash

### Script for aslprep singularity container
# Dylan Lawless
# Usage: run_aslprep: [--bidsdir] [--outdir] [--m0scan] [--aslscan] [--aslsource] [--examcard] [--fs_license]


# Initialize defaults
export bidsdir=NO_BIDS
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
    --bidsdir)
      export bidsdir="${2}"; shift; shift ;;
    --outdir)
      export outdir="${2}"; shift; shift ;;
    --m0scan)
      export m0scan="${2}"; shift; shift ;;
    --aslscan)
      export aslscan="${2}"; shift; shift ;;
    --examcard)
      export examcard="${2}"; shift; shift ;;
    --fs_license)
      export fs_license="${2}"; shift; shift ;;
    *)
      echo Unknown input "${1}"; shift ;;
  esac
done

#Get necessary data form exam card and write to json sidecar
/opt/xnatwrapper/examcard2json.py -i ${examcard} -s ${m0scan},${aslscan} -b ${bidsdir} 

#Create tsv file
/opt/xnatwrapper/create_tsv.py -b ${bidsdir}

#Run MRIQC
aslprep --fs-license-file ${fs_license} ${bidsdir} ${outdir} ${level} --skip_bids_validation

#Run py scripts to convert outputs
/opt/xnatwrapper/html2pdf.py -o ${outdir}