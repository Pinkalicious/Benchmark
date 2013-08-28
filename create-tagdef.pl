#!/usr/bin/perl

print "START=\$(date +%s) \n";
for ($i=1; $i < 5; $i++ ) {
	print "curl -w %{time_connect}#%{time_starttransfer}#%{time_total}\\\\n -k -H \"Authorization: Globus-Goauthtoken \$(cat goauth-token)\" -X PUT https://localhost/tagfiler/catalog/13/tagdef/test$i?dbtype=text&readpolicy=anonymous&multivalue=1&writepolicy=anonymous \n";
	print "sleep 1\n";
    }
	print "END=\$(date +%s) \n";
	print "DIFF=\$(( \$END - \$START ))\n";
	print "echo \"It took \$DIFF seconds\"\n";

