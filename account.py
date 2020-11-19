import forms
from db_connector import get_bsdb

class AccountSettings():
    """
    Methods for filling the forms on the `account` page.
    """

    def __init__(self, user_num):
        """
        Class initializer.
        Accepts:
            user_num (int): User id
        Returns:
            None
        """
        self.user_num = user_num
        self.bsdb = get_bsdb()

    def make_empty_password_change_form(self):
        """
        Creates and returns an empty password change form.
        """
        password_change_form = forms.PasswordChangeForm()
        return password_change_form

    def fill_account_settings_change_form(self):
        """
        Creates instance of the AccountSettingsChangeForm (form module),
            and fills it with relevant values.
        Accepts:
            Nothing
        Returns:
            Filled instance of AccountSettingsChangeForm (form module)
        """
        try:
            row = self.bsdb.get_account_settings(self.user_num)
            this_form = forms.AccountSettingsChangeForm()
            this_form.username.data = row['username']
            this_form.email.data = row['email']
            this_form.fName.data = row['fName']
            this_form.lName.data = row['lName']
            this_form.streetAddress.data = row['streetAddress']
            this_form.city.data = row['city']
            this_form.state.data = row['state']
            this_form.postCode.data = row['postCode']
            return this_form
        except KeyError:
            print("Account.py: Fill Account Settings Change Form error")
            return {}
        return {}

    def set_account_information(self, user_num, account_settings_change_form):
        """
        Changes account settings, aside from password, for given user.
        Accepts:
            user_num (int): Current logged in user number (Users.id)
            account_settings_change_form (AccountSettingsChangeForm instance)
        Returns:
            None on success, raises Exception on failure
        """
        req = {}
        req['username'] = account_settings_change_form.username.data
        req['email'] = account_settings_change_form.email.data
        req['fName'] = account_settings_change_form.fName.data
        req['lName'] = account_settings_change_form.lName.data
        req['streetAddress'] = account_settings_change_form.streetAddress.data
        req['city'] = account_settings_change_form.city.data
        req['state'] = account_settings_change_form.state.data
        req['postCode'] = account_settings_change_form.postCode.data
        try:
            self.bsdb.set_account_information(user_num, req)
        except Exception:
            raise Exception
        
    def is_username_valid(self, user_num, proposed_name):
        """
        Checks to see if requested username is available: either the same
            as current username, or not in database yet.
        Accepts:
            user_num (int): userId of current user
            proposed_name (string): proposed uesrname
        Returns:
            True if valid username, false otherwise
        """
        # First check to see if it's the same username
        current_name = self.bsdb.get_account_settings(user_num)['username']
        if current_name == proposed_name:
            return True

        # Now check if the user name is available
        return self.bsdb.is_username_available(proposed_name)
        
    def is_password_correct(self, user_num, password_change_form):
        """
        Checks to see if the given password is correct or not.
        Accepts:
            user_num (int): User.id
            password_change_form (PasswordChangeForm instance)
        Returns:
            True if the user supplied the correct original password,
                false otherwise.
        """
        try:
            return (password_change_form.old_password.data ==
                    self.bsdb.get_password(user_num))
        except Exception:
            raise Exception

    def set_password(self, user_num, password_change_form):
        """
        Changes user password.
        Accepts:
            user_num (int): User.i
            password_change_form (PasswordChangeForm instance)
        Returns:
            None
        """
        try:
            self.bsdb.set_password(user_num, password_change_form.new_password.data)
            return
        except Exception:
            raise Exception
        
