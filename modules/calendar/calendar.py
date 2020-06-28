#-*- coding: utf8 -*-
from datetime import datetime;
from modules.calendar.event_type import event_type;
from modules.calendar.event import event;
import re;
import pickle;
import os;
from collections import namedtuple;

#TODO regarder re.match() ...

class calendar(object):

    __STR_LIMIT__ = 255;

    # date_regex = re.compile("\[[0-9]+(-(1[0-2])|(0?[1-9]))?(-[0-3]?[0-9])?( (([0-1]?[0-9]|2[0-3]):[0-5][0-9]))?\]\&\".+\""); # not perfect but should be ok.
    YMD_regex = re.compile("([0-9]+-((1[0-2])|(0?[1-9]))-(3[0-1]|[0-2]?[0-9]))|((1[0-2])|(0?[1-9]))-((3[0-1])|([0-2]?[0-9]))|([0-2]?[0-9])");
    time_regex = re.compile("(([0-1]?[0-9])|(2[0-3])):[0-5][0-9]");
    event_name_regex = re.compile("[0-9aA-zZ]{1,30}")

    datetime_type = namedtuple("datetime_type", "type datetime");
    event_type_with_str = namedtuple("event_type_with_str", "datetime_type YMDT_str event_str");


    def __init__(self, event_file_path="modules/calendar/event_file.dic"):
        self.event_file_path = event_file_path;
        self.event_dic = {};
        try:
            if os.path.isfile(self.event_file_path):
                with open(self.event_file_path, "rb") as pickle_file:
                    self.event_dic = pickle.load(pickle_file);
        except:
            pass

    @classmethod
    def extract_time(cls, datetime_str):
        pass # regex here ;)

    @classmethod
    def parse_YMDT(cls, datetime_str):
        lg_str = 0 ; # this allows to check there is no additional substrings.
        ret = None;
        # Initialisation
        now = datetime.now();
        year, month, day = now.year, now.month, now.day;
        type = event_type.T;
        datetime_split = datetime_str.split("T");
        tmp_time, tmp_date = None, None;
        if len(datetime_split) == 1:
            T = re.fullmatch(calendar.time_regex, datetime_split[0]);
            if T:
                tmp_time = datetime_split[0];
            else:
                YMDT = re.fullmatch(calendar.YMD_regex, datetime_split[0]);
                if YMDT:
                    tmp_date = datetime_split[0];
                else:
                    ret = event_type.ERROR;
        elif len(datetime_split) == 2:
            YMDT = re.fullmatch(calendar.YMD_regex, datetime_split[0]);
            T = re.fullmatch(calendar.time_regex, datetime_split[1]);
            if YMDT and T:
                tmp_date, tmp_time = datetime_split[0], datetime_split[1];
            else:
                ret = event_type.ERROR;
        if ret: # no need to go further if parsing has failed.
            return ret;
        # Gestion de l'heure
        if tmp_time:
            time_split = tmp_time.split(":");
            hour, minute = int(time_split[0]), int(time_split[1]);
        else:
            hour, minute = 0, 0;
        # Gestion de la date
        if tmp_date:
            date_split = tmp_date.split("-");
            if len(date_split) == 3:
                type = event_type.YMDT;
                year, month, day = int(date_split[0]), int(date_split[1]), int(date_split[2])
            elif len(date_split) == 2:
                month, day = int(date_split[0]), int(date_split[1]);
                type = event_type.MDT;
            elif len(date_split) == 1:
                day = int(date_split[0]);
                type = event_type.DT;
        try:
            datetime_obj = datetime(year, month, day, hour, minute);
            ret = calendar.datetime_type(type, datetime_obj);
        except:
            ret = event_type.ERROR;
        return ret;

    # [2018-5-2]&[ANNIV]&[Anniversaire de tbot]
    def parse(self, cmd):
        brackets_check = lambda current_str : (current_str[0] == '[' and current_str[-1] == ']');
        remove_brackets = lambda current_str : (current_str[1:-1]);
        cmd_split = cmd.split('&');
        if len(cmd_split)!=3:
            return "";
        YMDT, event_name, event_string = cmd_split[0], cmd_split[1], cmd_split[2];
        ret = 0 ;
        # Parse YMDT
        error_YMDT = "Erreur : Il y a un problème avec la date de l'événement (format ou date passée)." ;
        if brackets_check(YMDT):
            YMDT = remove_brackets(YMDT);
            YMDT = calendar.parse_YMDT(YMDT);
            if (YMDT == event_type.ERROR):
                return error_YMDT;
            now = datetime.now();
            if (YMDT.type == event_type.YMDT) and (YMDT.datetime < now):
                return error_YMDT;
        else:
            return error_YMDT;
        # Parse event_name
        error_event_name = "Erreur : Le nom de l'événement ne doit comporter que des lettres (non accentuées) / nombres. Sa taille doit être comprise entre 1 et 30 caractères.";
        if brackets_check(event_name):
            event_name = remove_brackets(event_name);
            if not(re.search(calendar.event_name_regex, event_name)):
                return error_event_name;
        else:
            return error_event_name;
        # Parse event_string
        error_event_string = "Erreur : Il y a un problème avec le texte de l'événement (moins de {} caractères).".format(calendar.__STR_LIMIT__)
        if brackets_check(event_string):
            event_string = remove_brackets(event_string);
            if (len(event_string) > calendar.__STR_LIMIT__):
                return error_event_string;
        else:
            return error_event_string;
        ## Parsing is done ... Let's add the event !
        error_dic = "Erreur : L'événement existe déjà."
        if not(event_name in self.event_dic):
            self.event_dic[event_name] = event(YMDT.type, YMDT.datetime, event_string); # todo remove YMDT_str and make string from event_type.
        else:
            return error_dic;
        return "L'événement \"{}\" a bien été ajouté.".format(event_name)


    def save_event_dic(self):
        try:
            with open(self.event_file_path, "wb") as pickle_file:
                pickle.dump(self.event_dic, pickle_file);
            return "Les événements ont été sauvegardés."
        except RuntimeError as e:
            print(e);
            return "Une erreur s'est produite."

    def remove_event(self, event_name):
        if (event_name in self.event_dic):
            del self.event_dic[event_name];
            return "L'événement a bien été supprimé."
        else:
            return "Erreur : L'événement n'existe pas."

    def get_events(self):
        ret = "";
        for key, item in self.event_dic.items():
            print("coucou")
            ret += "- <b>[{}]</b>: {}".format(key, item);
            ret += '\n';
        return ret[:-1];



if __name__ == "__main__":
    YMDT_str = "1961-03-30"
    a = calendar.parse_YMDT(YMDT_str);
    print(a)
