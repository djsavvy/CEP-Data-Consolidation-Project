#!/bin/bash

DATABASES=(cep_hash cep_legacy cep_mol_test cep_perf cep_perf_legacy cep_pred cep_syn)

mkdir printable-parsed-output

for database in cep_hash cep_legacy cep_mol_test cep_perf cep_perf_legacy cep_pred cep_syn;
do
	echo "$database"
	cat $( ls parsed-output/ | grep "$database" | sort | awk '{print "parsed-output/" $0}') > printable-parsed-output/"$database".txt
done
