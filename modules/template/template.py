from modules.module import module ;

class template(module):

    def __init__(self, keyword = "template"): # <- template ... Here goes your default module name
        super().__init__(keyword) ;
        self.help = "Useless module" ; # <- will be printed out by the admin module
        self.whatis = "A simple template !"
        self.__version__ = "0.0.1"


    @module.check_command_dec
    @module.login_check_dec
    def process_msg_active(self, cmd, sender, room):
        # <-- Your code goes here.
        raw_args = cmd.split() ;
        if len(raw_args) == 3:
            if raw_args[2] == "Hello":
                return "Hello {}".format(sender) ;
        return None ;

    def process_msg_passive(self, cmd, sender, room):
        # <-- Your code goes here.
        raw_args = cmd.split() ;
        if len(raw_args) > 0:
            if raw_args[0] == "hi":
                return "Hi people !"

    @module.module_on_dec
    def run_on_clock(self):
        # <- Your code goes here.
        pass

    def exit(self):
        # <- Your code goes here.
        # This function is called when the bot is shut down,
        # this can for instance be used to save temporary variables into files.
        pass