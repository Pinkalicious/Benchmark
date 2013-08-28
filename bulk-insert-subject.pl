#!/usr/bin/perl

print "START=\$(date +%s) \n";
for ($i=102; $i < 10000; $i++ ) {
	print "curl -k -H \"Authorization: Globus-Goauthtoken \$(cat goauth-token)\" -X POST https://localhost/tagfiler/catalog/11/subject/name=yada$i\n";
    }
	print "END=\$(date +%s) \n";
	print "DIFF=\$(( \$END - \$START ))\n";
	print "echo \"It took \$DIFF seconds\n\"";

