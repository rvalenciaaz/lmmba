#! /usr/bin/env python3

from Bio.Seq import Seq
from Bio import SeqIO
import argparse

parser = argparse.ArgumentParser(description="Estadisticas para secuencias. Se requiere Python 3 y Biopython")
parser.add_argument('typ', metavar='type', type=str, nargs='+', help="Formato de archivo (fasta, fastq, etc...)")
parser.add_argument('secu', metavar='seq', type=str, nargs='+', help="Archivo con secuencias")
args = parser.parse_args()
namefi=args.secu[0]
tipe=args.typ[0]

i=0
c=0
maximo=0
minimo=float('Inf')
for seq_record in SeqIO.parse(namefi,tipe):
	i=i+1
	largo=len(seq_record)
	c=c+largo
	maximo=max(largo,maximo)
	minimo=min(largo,minimo)
print ('Reads:'+str(i))
print ('Total:'+str(round(c/1000000,3))+' Mbp')
print ('Promedio por reads:'+str(round(c/i,3)))
print ('Largo Maximo:'+str(maximo))
print ('Largo Minimo:'+str(minimo))
