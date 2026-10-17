# Unit tests for US5 Update user profile - write these FIRST (TDD)

# TODO UT5.1  test_ut5_1_isProfileNameTaken_ownName           -> ("Interior Designer", 2) False
# TODO UT5.2  test_ut5_2_isProfileNameTaken_otherName         -> ("Customer", 2) True
# TODO UT5.3  test_ut5_3_updateUserProfile_valid              -> True, changes saved
# TODO UT5.4  test_ut5_4_updateUserProfile_nameTaken          -> False, profile 2 unchanged
# TODO UT5.5  test_ut5_5_updateUserProfile_notFound           -> 9999 False, no error
# TODO UT5.6  test_ut5_6_updateUserProfile_emptyName          -> False
# TODO UT5.7  test_ut5_7_updateUserProfile_noPermissions      -> False
# TODO UT5.8  test_ut5_8_updateUserProfile_keepsStatus        -> True, still "Suspended"
# TODO UT5.9  test_ut5_9_validateInput_51chars                -> False
