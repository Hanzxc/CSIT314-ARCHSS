# Control: SearchUserAccountController - UC12 Search user account (US12)

from entity.userAccount import UserAccount


class SearchUserAccountController:
    # UT12.1 to UT12.6
    def searchUserAccounts(self, keyword):
        # same as US7 - "  chloe  " works like "chloe", and just spaces counts as empty
        if keyword is None:
            keyword = ""
        keyword = keyword.strip()

        accounts = UserAccount().searchUserAccounts(keyword)
        return accounts
