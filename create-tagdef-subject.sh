#!/bin/bash
rm tagdefdel_time
for var in {5..25}
do
curl -w %{time_connect}#%{time_starttransfer}#%{time_total}\\n -k -H "Authorization: Globus-Goauthtoken $(cat goauth-token)" -X DELETE https://localhost/tagfiler/catalog/13/tagdef/test$var >> tagdefdel_time
done
cut -f3 -d'#' tagdefdel_time | paste -sd+ | bc

python create-tagdef-subject.py `cat goauth-token` 13 6 26 5 1 10000 10000 10
paste -sd+ tagdef_time | bc
paste -sd+ subject_time | bc
