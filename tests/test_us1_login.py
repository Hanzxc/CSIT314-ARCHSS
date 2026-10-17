# Unit tests for US1 Log in - write these FIRST (TDD), then code until they pass
# test data: admin01 / Admin@123 (Active), admin02 (Suspended account), cust001 / Cust@123 (Customer)

# TODO UT1.1  test_ut1_1_verifyCredentials_correct        -> returns admin01's UserAccount
# TODO UT1.2  test_ut1_2_verifyCredentials_wrongPassword  -> None
# TODO UT1.3  test_ut1_3_verifyCredentials_noSuchUser     -> None
# TODO UT1.4  test_ut1_4_verifyCredentials_empty          -> None, no error
# TODO UT1.5  test_ut1_5_isActive_suspendedAccount        -> False
# TODO UT1.6  test_ut1_6_login_correct                    -> UserAccount (not None)
# TODO UT1.7  test_ut1_7_login_accountSuspended           -> None
# TODO UT1.8  test_ut1_8_login_profileSuspended           -> None
# TODO UT1.9  test_ut1_9_validateInput_emptyPassword      -> False
# TODO UT1.10 test_ut1_10_validateInput_filledIn          -> True
