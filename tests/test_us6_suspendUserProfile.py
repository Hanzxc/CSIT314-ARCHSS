# Unit tests for US6 Suspend user profile - write these FIRST (TDD)

# TODO UT6.1  test_ut6_1_suspendUserProfile_valid             -> (3, 1) True, status "Suspended"
# TODO UT6.2  test_ut6_2_suspendUserProfile_alreadySuspended  -> False
# TODO UT6.3  test_ut6_3_suspendUserProfile_ownProfile        -> (1, 1) False, still Active
# TODO UT6.4  test_ut6_4_suspendUserProfile_notFound          -> (9999, 1) False, no error
# TODO UT6.5  test_ut6_5_isActive_afterSuspend                -> False
# TODO UT6.6  test_ut6_6_login_afterSuspend                   -> cust001 can't log in, None
# TODO UT6.7  test_ut6_7_suspend_keepsAccounts                -> same number of accounts in profile 3
