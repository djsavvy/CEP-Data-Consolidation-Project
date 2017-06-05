# Field Tree Visualization

This is a compilation of all the fields in all the collections in all the CEP databases in the existing MongoDB server. 

## cep_hash 

- calculation
	- \_id
	- meta_data
		- key
		- data_type
		- smiles
		- atom_list
		- annotation_list
		- tag_list
		- user_defined_list
		- user_defined_dict
		- document_creation_date
		- document_update_date
	- molecule
	- descriptor_list
	- calculation_type_list
	- file_list
	- parent_calculation_list
	- child_calculation_list 
	- coord_list
	- orbital_energy_list
	- normal_mode_list
	- excited_states
	- velocity_list
	- properties *(note: some records only have the 7 italicized properties below)*
		- total_energy
		- total_nuclear_energy
		- homo
		- lumo
		- gap
		- *unrestricted_homo_list*
		- *unrestricted_lumo_list*
		- *unrestricted_gap_list*
		- *unrestricted_occupied_orbital_number*
		- power_conversion_efficiency
		- open_circuit_voltage
		- short_circuit_current_density
		- *rmsd_w_parent_list*
		- *sites*
		- *distance_matrix*
	- user_defined_properties
	- user_defined_property_dict
	- user_defined_property_list

- molecule
	- \_id
	- meta_data
		- key
		- data_type
		- smiles
		- atom_list
		- annotation_list
		- tag_list
		- user_defined_list
		- user_defined_dict
		- document_creation_date
		- document_update_date
	- diagram_list
	- calculation_list
	- reactive_mol_list
	- file_list
	- descriptor_list
	- parent_list
	- child_list
	- nickname_list


## cep_legacy

- 
