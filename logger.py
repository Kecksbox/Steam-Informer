import time

# Set the name of the logfile
log_file = time.strftime("%Y.%m.%d") + '.log'


def log(text, module_name='unknown'):
    """This function logs a text to a logfile and to the console itself.
       It gets a module_name like 'logger' which gets processed to '[logger]' and a text"""

    global log_file

    # Set the text which will be logged
    log_text = '(' + time.strftime("%Y.%m.%d-%H.%M.%S") + ')' + '[' + module_name + ']: ' + text

    # Write the log_text to the logfile
    with open(log_file, 'a') as file:
        file.write(log_text + '\n')

    # Write the log_text to the console
    print(log_text)


def log_download(source, data_type="unknown", module_name='unknown'):
    """This function logs download data with the use of a specific style to the logfile and to the console itself."""

    global log_file

    # Set the current time
    time_date = time.strftime("%Y.%m.%d-%H.%M.%S")

    # Create the text that should be logged
    log_text = """-------------------------------------------------------------------------------
({time_date})[{module_name}] >>> Downloading ({data_type}) : {source}
-------------------------------------------------------------------------------""".format(source=source, data_type=data_type, time_date=time_date, module_name=module_name)

    # Write the log_text to the logfile
    with open(log_file, 'a') as file:
        file.write(log_text + '\n')

    # Write the log_text to the console
    print(log_text)
