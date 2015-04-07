#!/usr/bin/perl 

  use CGI;
  use CGI::Session;
  use CGI::Session::Auth;

  # CGI object for headers, cookies, etc.
  my $cgi = new CGI;

  # CGI::Session object for session handling
  my $session = new CGI::Session(undef, $cgi, {Directory=>'/tmp'});

  # CGI::Session::Auth object for authentication
  my $auth = new CGI::Session::Auth({ CGI => $cgi, Session => $session });
  $auth->authenticate();
  
   print "Content-type: text/html\n\n";
# uid | name |               pass               |    mail     | mode | sort | threshold | theme | signature | signature_format |  created   |   access   |   login    | status | timezone | language | picture |    init     |                                   data
#-----+------+----------------------------------+-------------+------+------+-----------+-------+-----------+------------------+------------+------------+------------+--------+----------+----------+---------+-------------+--------------------------------------------------------------------------
#   1 | vty  | 6f8522e0610541f1ef215a22ffa66ff6 | vty@iisg.nl |    0 |    0 |         0 |       |           |                0 | 1319466432 | 1344591987 | 1344591987 |      1 | 7200     |          |         | vty@iisg.nl | a:1:{s:13:"form_build_id";s:37:"form-7a68937fefe14a9cde0b32ef4fb448dd";}

   print $session->header();

  # check if visitor has already logged in
  if ($auth->loggedIn) {
      #showSecretPage;
	print "Logged it\n";
  }
  else {
      #showLoginPage;
	print "No logged it\n";
  }
