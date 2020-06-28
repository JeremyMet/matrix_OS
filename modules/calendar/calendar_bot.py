from modules.module import module ;
from .calendar import calendar;
import datetime;

class calendar_bot(module):

        def __init__(self, keyword = "calendar", event_file_path="modules/calendar/event_file.dic"): # <- template ... Here goes your default module name
            super().__init__(keyword) ;
            self.help = "WIP" ; # <- will be printed out by the admin module
            self.whatis = "A Calendar module. "
            self.module_name = "Calendar Module"
            self.__version__ = "0.0.1"
            self.calendar_inst = calendar();


        @module.module_on_dec
        def process_msg_active(self, cmd, sender=None, room=None):
            raw_cmd = cmd.split(" ");
            ret = "" ;
            if (len(raw_cmd) == 4 and raw_cmd[2] == "delete"):
                ret = self.calendar_inst.remove_event(raw_cmd[3]);
            if (len(raw_cmd) == 3 and raw_cmd[2] == "save"):
                ret = self.calendar_inst.save_event_dic();
            if (len(raw_cmd) == 3 and raw_cmd[2] == "get_events"):
                ret = self.calendar_inst.get_events();
            return ret ;

        @module.module_on_dec
        def process_msg_passive(self, cmd, sender=None, room=None):
            ret = self.calendar_inst.parse(cmd);
            return ret;

        @module.module_on_dec
        # @module.clock_dec
        def run_on_clock(self):
            pass
            # log = self.calendar_inst.get_log();

        def exit(self):
            print("\tSauvegarde en cours ...")
            # self.loto_inst.save_current_state();