#!/bin/bash
# script qui change le nom des sequences dans le fichier d'alignement de MAFFT en remplacant les "espaces" par "_", utile pour fasttree. si les nom n'ont pas despaces, pas besoin d'utiliser ce script 

for file in "$@"; do
    echo "rename $file"
    sed -i '/^>/ s/ /_/g' "$file"
done
