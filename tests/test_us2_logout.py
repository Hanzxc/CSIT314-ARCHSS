# Unit tests for US2 Log out - write these FIRST (TDD)
# logout() uses the flask session, so run these inside app.test_request_context()

# TODO UT2.1  test_ut2_1_logout_loggedIn     -> True, session has no userId after
# TODO UT2.2  test_ut2_2_logout_notLoggedIn  -> False, no error
# TODO UT2.3  test_ut2_3_logout_twice        -> True then False
