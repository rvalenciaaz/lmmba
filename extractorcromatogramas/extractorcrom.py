#! /usr/bin/env python3
from PyPDF2 import PdfFileWriter, PdfFileReader

from os import listdir
from os.path import isfile, join
#from joblib import Parallel, delayed
import multiprocessing
import subprocess
import argparse
import tabula
import pandas as pd
from functools import reduce
from tqdm import tqdm

num_cores=multiprocessing.cpu_count()

parser = argparse.ArgumentParser(description="Extractor de valores desde cromatogramas de GC-FID. Escrito en Python 3.5. Se requiere los paquetes pandas, tabula, PyPDF2 y tqdm")
parser.add_argument('directory', metavar='dir', type=str, nargs='+', help="Directorio donde se encuentran los cromatogramas en formato pdf (sin slash)")
parser.add_argument('output', metavar='out', type=str, nargs='+', help="Archivo de salida con los valores en formato csv (sin extension)")
args = parser.parse_args()
fol=args.directory[0]+'/'
outf=args.output[0]

onlyfiles = [f for f in listdir(fol) if (isfile(join(fol, f)) and f[-8:]!='crop.pdf')]

def crop(names):
	with open(fol+names, "rb") as in_f:
		input1 = PdfFileReader(in_f)
		output = PdfFileWriter()

		numPages = input1.getNumPages()
		#print "document has %s pages." % numPages

		for i in range(numPages):
			page = input1.getPage(i)
			if i==0:
				page.scale(1.5,1.5)
				page.cropBox.lowerLeft = (0, 0)
				page.cropBox.upperRight = (page.mediaBox.getUpperRight_x(),380)
		
				output.addPage(page)
			else:
				page.scale(1.5,1.5)
				page.cropBox.lowerLeft = (0,300)
				page.cropBox.upperRight = (page.mediaBox.getUpperRight_x(),page.mediaBox.getUpperRight_y())
				output.addPage(page)
		
		with open(fol+names.split('_')[2][0:-4]+'crop.pdf', "wb") as out_f:
			output.write(out_f)
	in_f.close()
	out_f.close()

#Parallel(n_jobs=num_cores)(delayed(crop)(i) for i in onlyfiles)
print ("Creando archivos recortados ...")
for archivo in tqdm(onlyfiles):
	crop(archivo)



onlycrop= [f for f in listdir(fol) if (isfile(join(fol, f)) and f[-8:]=='crop.pdf')]

j=1
pro=[]
print ("Extrayendo valores ...")
for i in tqdm(onlycrop):
	
	out=tabula.read_pdf(fol+i,pages='all', multiples_tables=1)
	out=out[['Component','Area']]
	out=out.dropna(how='any',subset=['Component'])
	out=out[out.Component!='Component']
	out=out[out.Component!='Name']
	out=out[out.Component.str[0]!=':']
	out=out.dropna(how='any',subset=['Area'])
	out.columns=['Component',i[0:-8]]
	pro.append(out)
	#print (i+' '+str(j)+' '+str(len(out)))
	j=j+1

df_final = reduce(lambda left,right: pd.merge(left,right,on='Component', how='outer'), pro)

df_final.to_csv(outf+'.csv', index=False)

