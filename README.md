# Matrix_Bot

Matrix_Bot is a simple Python library that **facilitates service deployment** across Matrix Rooms.
Services (or modules) are Python scripts which process room sent messages. For instance, a message can ask a given module *A* to print out the current weather. Matrix_Bot will then interpret the order and ask module *A* to return the desired information. Matrix_Bot is mainly a **small framework for "chat bot"**.

## Security Note

Poor understanding of the tool could lead to severe security issues (malicious codes that could erase one's hard drive, leak and display of plain passwords etc). First, matrix_bot **must** be dockerized to limit attack vectors. Plus, the *admin* module (see below) should be built-in in a trusted private room.

## How does it work ?

The following snippet gives a quick overview of Matrix_OS functionnalities:

```python
    my_pendu = pendu_bot("pendu", is_permanent = True) ;
    # my_pendu.set_clock_sensitivity_on() ;
    my_greeting = greeting("greeting") ;
    my_admin_0 = admin("admin", is_permanent = True) ;
    my_admin_1 = admin("admin", is_permanent = True);
    my_quotes = quotes("quotes") ;
    my_template = template()
    my_regex = regex() ;
    # Then Create the matrix object, add rooms, services and timers.
    matrix_obj = matrix_utils() ;
    gaming_room = matrix_obj.add_room("#toto-gaming:mandragot.org")
    main_room = matrix_obj.add_room("#toto:mandragot.org")

    # Add timer to services
    # Add services :)
    matrix_obj.add_service_to_room(main_room, my_regex)

    matrix_obj.add_service_to_room(gaming_room, my_pendu) ;
    matrix_obj.add_service_to_room(gaming_room, my_greeting);

    # Start timer
    matrix_obj.remove_service_from_room(gaming_room, my_pendu)
    matrix_obj.add_timer_to_service(my_admin_1);
    # matrix_obj.remove_service_from_room(main_room, my_admin_1)
    matrix_obj.start_timer()
    # And run
    matrix_obj.spawn() ; 
```
First, one instantiates modules. 
All modules inherit from the class *module*. When instantiating a module, one can specify a module name. This module name *$MODULE_NAME* is the one that will be used to call the corresponding service once installed in a chat room. Two modules with the same module name can not be installed in a same room (that would result to conflicting calls). An additive flag (namely *is_permanent*) allows a module to be permanent, meaning that no one can deactivate it or desinstall it (see admin module, below).

The modules should follow a specific structure (that you may find in the modules/template folder). Each module is composed of (at least) four methods, two (*process_msg_active* and *process_msg_passive*) that will be in charged of "message processing", one (*run_on_clock*) that will be activated every second (that you may use to display weather every hour of the day) and one (*exit*) that will be called when the service is shut down (this can be useful to save temporary variables into files).

There is a clear distinction between *process_msg_active* and *process_msg_passive* methods. The former is called through a *"tbot $MODULE_NAME"* instruction (entered in the room where the module is set up) while the latter processes other messages (what we name passive listening). 

Decorator @module.login_check_dec in front of *both process_msg_active* and *process_msg_passive* methods prevent them from processing bot's own messages. Nonetheless, this decorator can be removed (it may be sometimes useful to listen to the bot's own words).

Then, the matrix object is created. It will load login information (server/login/password) from *config.json* file.
One can finally add rooms and services before running matrix_os bot (*matrix_obj.spawn()*).

Internal clock (that ticks every second) should be set on in case you have modules that may be clock sensitive. To do so, just type the *matrix_obj.start_timer()* instruction. The ticks can be stopped thanks to the *matrix_obj.stop_timer()* command.

Note that each room "lives" independently in a sense that each room does have its own service list. Services can be shared between room. Please, understand that sharing service between rooms can lead to undesirable behaviour and should be thought with care beforehand. For many reasons (including security issues), it is **preferable** to dockerize the matrix_bot. As you will later see, one can install modules on-the-fly thanks to the admin module. These modules could be malicious as they could for instance erase all your system files ... That is why **docker** is very important here.

All services are "clock insensitive" by default (meaning their *run_on_clock* subroutines will **not** be called once per second). This sensitivity of modules can be switched on (*matrix_obj.add_timer_to_service(service)*) or switched off (*matrix_obj.remove_timer_to_service(service)*) separately.

In a matrix room in which module *A* has been installed, one simply has to write *tbot A* to call the *A* module.
Of course, parameters can be added to the message as *tbot A parameter_0 parameter_1 ... parameter_n* but this input should be manually parsed/processed in the *run* method.

## Admin module

This module is a powerful one. It should not be instantiated in sensitive rooms as this module allows to install/desinstall/activate/deactivate modules.  

1. To **install** a new module from url, type the following
```
tbot admin install $MODULE_NAME https://gist.githubusercontent.com/JeremyMet/4016c881ae7b7e988fec542a4a04e470/raw/8faafe527e69cce48bbf1c9fc2e4b624b1bee5bc/template.py
```

2. To **install** a set of modules from a specified list
```
tbot admin install_from_list $URL
```

URL should target a text file that must conform to the following syntax:

```
module_0==https://mywebsite.org/module.py
module_1==https://mywebsite.org/print_all.py
```

Names *module_0* and *module_1* are the service names respectively given to module.py instance/print_all.py instance. It will then be sufficient to type "tbot module_0" to call the service *module_0*.

3. To **list** all rooms:
```
tbot admin room_list
```

4. To **list** all services in a room:
```
tbot admin service_list
```

5. To push string to the admin's module stack:
```
tbot admin push "your string"
```

6. To pop string from the admin's module stack:
```
tbot admin pop
```

Commands 5. and 6. can be handy as you can store several instructions on the stack. For instance, you can write the following,
```python
tbot admin push "tbot admin service_list \n tbot admin pop"
tbot admin push "tbot admin room_list \n tbot admin pop"
```
and then write *tbot admin pop*. The bot will then return both *tbot admin service_list* AND *tbot admin pop*. This last instruction asks the bot to pop another string, namely *tbot admin room_list* AND *tbot admin pop*. If the stack is empty, the latter would return "Stack is empty". This behaviour is powerful to create "chain reaction".

The module also includes an "auto restart" option that allows to "reboot the bot" once a day at a specific time. This can be configured thanks to the *config.json* file located in the admin folder.

## Regex Module

Regex Module is a simple module which allows to save a regular expression and an excepted output along side.
The *tbot regex "[hH]ello" "Hello friend"*  instruction would store the regex "[hH]ello". Since then, the bot would answer "Hello friend" every single time it reads "hello"/"Hello" from chat room. 
Such a feature could be used to create aliases, i.e. making wordy instructions smaller. As an example, one could type "tbot regex "room_list" "tbot admin room_list". By typing "room_list", the regex module will answer back "tbot admin room_list". As the admin module listens to bot's own word, it will then execute the "tbot admin room_list" and display the excepted result.

```
tbot regex $REGEX $OUTPUT
```

## Any Module

Every module that you will write will inherit from the class *module*. This class integrates in-built features, as *tbot $MODULE_NAME uninstall* to uninstall a module. The service object itself will not be deleted but it will not be executed anymore through message event callback functions. Module can also be deactivated *tbot $MODULE_NAME deactivate*. The module will be in "sleep mode" and can be reactivated any time soon thanks to the *bot $MODULE_NAME activate* function.
