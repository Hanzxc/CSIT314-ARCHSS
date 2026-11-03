# Control: SearchUserAccountController - UC12 Search user account (US12)

from entity.userAccount import UserAccount


class SearchUserAccountController:
    # UT12.1 to UT12.6
    # the page already tidied the keyword (spaces trimmed), so just pass it on
    def searchUserAccounts(self, keyword):
        return UserAccount().searchUserAccounts(keyword)
