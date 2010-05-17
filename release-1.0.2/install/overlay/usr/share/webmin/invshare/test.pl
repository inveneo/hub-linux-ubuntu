use share; 

use Test::Simple tests => 15; 

ok( is_valid_share_name('abc') );
ok( is_valid_share_name('123') );
ok( is_valid_share_name('ab1') );
ok( !is_valid_share_name('ab[]') ); 

ok( convert_to_share_dir_name('TEST') eq 'test' );
ok( convert_to_share_dir_name('TeSt123') eq 'test123' ); 
ok( convert_to_share_dir_name('Test 123') eq 'test^123' ); 
ok( convert_to_share_dir_name('TeSt_123') eq 'test_123' ); 

ok( share_exists("shared_docs") );
ok( !share_exists("dne") );
ok( !share_exists("!!@!@#") ); 

@shares = get_share_names("./testdata");
print "num shares: " .  @shares, "\n";
ok( @shares == 2 );
ok( $shares[0] eq 'share1' ); 
ok( $shares[1] eq 'share2' ); 

@shares = get_share_names(".");
print "num shares: " . @shares, "\n";
ok( @shares == 0 );
