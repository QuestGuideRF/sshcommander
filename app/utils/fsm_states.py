from aiogram .fsm .state import State ,StatesGroup
class AddServer (StatesGroup ):
    name =State ()
    ip =State ()
    port =State ()
    login_user =State ()
    password =State ()