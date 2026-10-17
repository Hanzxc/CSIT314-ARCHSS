# Unit tests for US3 Create user profile - write these FIRST (TDD)

# TODO UT3.1  test_ut3_1_getAllPermissions                -> 8 permissions
# TODO UT3.2  test_ut3_2_isProfileNameTaken_existing      -> "Customer" True
# TODO UT3.3  test_ut3_3_isProfileNameTaken_capitals      -> "cUSTOMER" True
# TODO UT3.4  test_ut3_4_isProfileNameTaken_new           -> "Customer Support" False
# TODO UT3.5  test_ut3_5_createUserProfile_valid          -> True, saved as "Active"
# TODO UT3.6  test_ut3_6_createUserProfile_nameTaken      -> False, count unchanged
# TODO UT3.7  test_ut3_7_createUserProfile_emptyName      -> False
# TODO UT3.8  test_ut3_8_createUserProfile_noPermissions  -> False
# TODO UT3.9  test_ut3_9_validateInput_2chars             -> "AB" False
# TODO UT3.10 test_ut3_10_validateInput_3chars            -> "Ops" True
# TODO UT3.11 test_ut3_11_validateInput_50chars           -> True
# TODO UT3.12 test_ut3_12_validateInput_51chars           -> False
