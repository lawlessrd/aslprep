#!/bin/bash

### Script for aslprep singularity container
# Dylan Lawless
# Usage: run_aslprep: [--bidsdir] [--outdir] [--scan_names] [--examcard] [--fs_license]


# Initialize defaults
export bidsdir=NO_BIDS
export outdir=NO_OUTDIR
export level=participant
export wrkdir=NO_WRKDIR
export scan_names=NO_SCANNAMES
export examcard=NO_EXAMCARD

# Parse options
while [[ $# -gt 0 ]]; do
  key="${1}"
  case $key in
    --bidsdir)
      export bidsdir="${2}"; shift; shift ;;
    --outdir)
      export outdir="${2}"; shift; shift ;;
    --scan_names)
      export scan_names="${2}"; shift; shift ;;
    --examcard)
      export examcard="${2}"; shift; shift ;;
    --fs_license)
      export fs_license="${2}"; shift; shift ;;
    *)
      echo Unknown input "${1}"; shift ;;
  esac
done

#Get necessary data form exam card and write to json sidecar
/opt/xnatwrapper/examcard2json.py -i ${examcard} -s ${scan_names} -b ${bidsdir} 

#Create tsv file
/opt/xnatwrapper/create_tsv.py -b ${bidsdir}

#Run MRIQC
aslprep --fs-license-file ${fs_license} ${bidsdir} ${outdir} ${level} 

#Run py scripts to convert outputs
/opt/xnatwrapper/html2pdf.py -o ${outdir}