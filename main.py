from os import path, getcwd
import sys
from json import load, dump
from xmltodict import parse
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from tkinter import Label, Button, Entry, Tk


def resource_path(relative_path):
    """ Get absolute path to resource, needed for exe compilation """
    base_path = getattr(sys, '_MEIPASS', path.dirname(path.abspath(__file__)))
    return path.join(base_path, relative_path)


# create the root window in tkinter
root = Tk()
root.iconbitmap(resource_path("LSL_ico.ico"))
root.title('BVEF Coordinate Injector for LSL')
root.resizable(False, False)
root.geometry('350x200')

BVEF = ""
LSL = ""


def select_file_BVEF():
    global BVEF
    global root

    filetypes = (
        ('BVEF files', '*.bvef'),
        ('All files', '*.*')
    )

    BVEF = fd.askopenfilename(
        title='Open a file',
        initialdir=getcwd(),
        filetypes=filetypes)

    # update filename entry
    new_BVEF = "..." + BVEF[-50:]
    bvef_entry = (Entry(root, width=50))
    bvef_entry.grid(row=0, column=0, padx=5, pady=5)
    bvef_entry.insert(0, new_BVEF)
    bvef_entry.config(state="disabled")  # prevent input, we won't read it


def select_file_LSL():
    global LSL
    global root

    filetypes = (
        ('JSON files', '*.json'),
        ('All files', '*.*')
    )

    LSL = fd.askopenfilename(
        title='Open a file',
        initialdir=getcwd(),
        filetypes=filetypes)

    # update filename entry
    new_LSL = "..." + LSL[-50:]
    lsl_entry = (Entry(root, width=50))
    lsl_entry.grid(row=2, column=0, padx=5, pady=5)
    lsl_entry.insert(0, new_LSL)
    lsl_entry.config(state="disabled")  # prevent input, we won't read it


def inject():
    # parse bvef file

    try:  # load the BVEF file as XML
        with open(BVEF, 'r', encoding='utf-8-sig') as f:
            bvef_file = f.read()
    except:  # if we cannot open the BVEF file, one was likely not selected
        showinfo(
            title='Error',
            message="BVEF File Not Found!"
        )
        return  # try again

    electrodes = parse(bvef_file)['Electrodes']['Electrode']  # list of dicts containing electrode info
    for i in range(len(electrodes) - 1, -1, -1):  # for each electrode (from highest to lowest)...
        if 'Number' not in electrodes[i].keys():   # if the electrode does not have a number...
            electrodes.pop(i)  # remove marked channels. This will target GND and REF channels
    # electrodes now contains a list of dicts formatted as follows:
    # {'Name': 'Fp1',   channel 10-20 label
    # 'Theta': '-90',   coordinates
    # 'Phi': '-72',     coordinates
    # 'Radius': '1',    coordinates
    # 'Number': '1'}    channel number for amplifier

    # parse json file
    try:
        with open(LSL, 'r') as file:
            data = load(file)
    except:  # if we cannot open the LSL file, one was likely not selected
        showinfo(
            title='Error',
            message="LSL Configuration File Not Found!"
        )
        return  # try again

    for chan in data['Amplifier']['Channels']:  # for each channel...
        # each chan is formatted as follows:
        #{'ChannelNumber'   : 10,                   module specific, which changes for each amplifier. Usually not >32
        # 'HighPass'        : 0,                    filter parameter
        # 'Index'           : 10,                   product of module and channel number. Can increase indefinitely
        # 'Label'           : 'EEG 1_11',           text label of channel
        # 'LowPass'         : 65,                   filter parameter
        # 'ModuleNumber'    : 0,                    which module the channel is in (module numbers vary by amplifier)
        # 'RecordingEnabled': True,                 is this channel turned on
        # 'Resolution'      : 0.0406901054084301,   amplifier specific value
        # 'Type'            : 0}                    channel type, with 0 = EEG

        for electrode in electrodes:  # search for the matching electrode label
            if chan['Index'] == int(electrode['Number'])-1 and chan['Type'] == 0:  # if channel index matches electrode number (EEG only)...
                chan['Label'] = electrode['Name']  # assign the correct name
                break  # we need not continue once the match is found

    # write new file
    filename = LSL[:-5] + "_modified.json"  # create new file as to not overwrite previous
    with open(filename, "w") as f:
        dump(data, f, indent=4)

    # Display the name of the created file
    new_filename = "Output: ..." + filename[-40:]
    label_Output_filename = Label(root, text=new_filename)
    label_Output_filename.grid(row=5, column=0, padx=5, pady=2)

    showinfo(
        title='',
        message="All BVEF channel names inserted!"
    )


def main():
    # close splash screen for executable
    try:
        import pyi_splash
        pyi_splash.close()
    except:
        pass

    # File selector for BVEF
    bvef_button = Button(
        root,
        text='Select BVEF File (.bvef)',
        command=select_file_BVEF
    )

    # Text label to display selected BVEF file
    bvef_entry = Entry(root, width=50)
    bvef_entry.config(state="disabled")  # prevent input, we won't read it

    # File selector for JSON
    lsl_button = Button(
        root,
        text='Select LSL Configuration File (.json)',
        command=select_file_LSL
    )

    # Text label to display selected LSL configuration file
    lsl_entry = Entry(root, width=50)
    lsl_entry.config(state="disabled")  # prevent input, we won't read it

    # Button to Start
    start_button = Button(
        root,
        text="Inject",
        command=inject
    )

    # Assemble grid
    bvef_entry.grid(row=0, column=0, padx=5, pady=5)
    bvef_button.grid(row=1, column=0, padx=75, pady=5)
    lsl_entry.grid(row=2, column=0, padx=5, pady=5)
    lsl_button.grid(row=3, column=0, padx=75, pady=5)
    start_button.grid(row=4, column=0, padx=5, pady=5)

    root.mainloop()


if __name__ == "__main__":
    main()
