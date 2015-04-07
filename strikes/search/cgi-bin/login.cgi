#!/usr/bin/perl

use CGI;
use CGI::Session;
use CGI::Session::Driver::DBI;
use CGI::Session::Auth::DBI;

my $cgi = new CGI;
my $session = new CGI::Session(undef, $cgi, {Directory=>'/tmp'});

#infraclio:infra911@localhost/clioinfra.alpha
$s = CGI::Session->new('driver:Pg', undef,
{
DataSource => 'dbi:Pg:host=localhost,database=clioinfra.alpha',
TableName => 'drpl_sessions',
IdColName => 'sid',
DataColName => 'session',
});

my $auth = new CGI::Session::Auth::DBI({
CGI => $cgi,
Session => $s,
DSN => 'dbi:Pg:host=localhost,database=clioinfra.alpha',
DBUser => 'infraclio',
DBPasswd => 'infra911',
UserTable => 'drpl_users',
UserIDField => 'uid',
UsernameField => 'name',
PasswordField => 'pass',
GroupTable => 'drpl_users_roles',
GroupField => 'rid',
GroupUserIDField => 'uid',
});

$auth->authenticate();

if ($auth->loggedIn) {
showSecretPage;
}
else {
showLoginPage;
}

