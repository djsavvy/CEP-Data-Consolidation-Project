#!/bin/bash

while [[ $# -gt 1 ]]
do
key="$1"

case $key in
	-u|--username)
	MONGOUSER="$2"
	shift
	;;
	-p|--password)
	PASSWORD="$2"
	shift
	;;
esac
shift
done

DATABASES=(adorsk_foo cep_hash cep_legacy cep_mol_test cep_perf cep_perf_legacy cep_pred cep_syn cep_szvvy_test)

for database in $DATABASES;
do
	echo python3 migrator.py --username "${MONGOUSER}" --password "${PASSWORD}" --db "${database}"
	python3 migrator.py --username "${MONGOUSER}" --password "${PASSWORD}" --db "${database}"

done
