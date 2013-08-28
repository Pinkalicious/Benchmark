#!/usr/bin/perl

print "START=\$(date +%s) \n";
$start = $ARGV[0];
$end = $ARGV[1];
$ctg = $ARGV[2];
$prefix = $ARGV[3];
for ($i=$start; $i < $end; $i++ ) {
	print "curl  -w %{time_connect}#%{time_starttransfer}#%{time_total}\\\\n -k -H \"Authorization: Globus-Goauthtoken \$(cat goauth-token)\" -X DELETE https://localhost/tagfiler/catalog/$ctg/tagdef/test$prefix$i\n";
	print "sleep 1 \n";  
    }
	print "END=\$(date +%s) \n";
	print "DIFF=\$(( \$END - \$START ))\n";
	print "echo It took \$DIFF seconds\n";

