#!/usr/bin/env python3

# * remember input dir & output dir
# * don't throw error when no file input
# * Windows icoon in taakbalk & venster
# * Windows Installer icoon
# * Mac About overnemen
# * Mac quit verbergen
# * Mac Info-menubalk in globale bar verwerken

import csv
from datetime import datetime
import os
import platform
import re
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser

version = "20190112"

############################################################################
#
# ING
#
############################################################################

def ing_decode_paymentmode(x):
      return {
          'AC': 4,  # AC = Acceptgiro => 4 = Transfer
          'IC': 11, # IC = Incasso => 11 = Direct Debit
          'BA': 6,  # BA = Betaalautomaat => 6 = Debit card
          'OV': 4,  # OV = Overschrijving => 4 = Transfer
          'PK': 3,  # PK = Opname kantoor => 3 = Cash
          'FL': 4,  # FL = Filiaalboeking => 4 = Transfer
          'PO': 7,  # PO = Periodieke overschrijving => 7 = Standing Order
          'GF': 8,  # GF = Telefonisch bankieren => 8 = Electronic Payment
          'ST': 9,  # ST = Storting => 9 = Deposit
          'GM': 3,  # GM = Geldautomaat => 3 = Cash
          'VZ': 4,  # VZ = Verzamelbetaling => 4 = Transfer
          'GT': 8,  # GT = Internet bankieren => 8 = Electronic Payment
      }.get(x, 0)   # DV = Diversen => 0 = no payment type assigned


def ing_parse(transactions):
    transactions.pop(0) # remove column row

    out = []
    for item in transactions:
        
        date = datetime.strptime(item[0],"%Y%m%d").strftime("%m/%d/%Y") # Datum, from YYYYMMDD to MM/DD/YY
        
        if item[4] == 'DV' and item[3] =='' and 'INCASSO CREDITCARD ' in item[1]:
            paymode = 1 # credit card payments don't have a specific code in ING's CSV
        else:
            paymode = ing_decode_paymentmode(item[4])
        
        info = item[4]
        
        payee = ''.join(item[1].split("\n")) # Naam/Omschrijving
        if item[3] != '':
            payee += ' ['+item[3]+']' # Tegenrekening
        
        desc = ''.join(item[8].split("\n")) # Mededelingen
        
        amount = str(item[6])
        if item[5] == "Bij": # Af/Bij
            amount = '-'+amount # Bedrag (EUR)

        cat = ''
        
        tag = ''
        
        out.append( [date, paymode, info, payee, desc, amount, cat, tag] )

    return out

############################################################################
#
# ASN
#
############################################################################

def asn_decode_paymentmode(x):
      return {
          'ACC':  4, # ACC Acceptgirobetaling 4
          'AF':   4, # AF  Afboeking 4
          'AFB':  7, # AFB Afbetalen 7
          'BEA':  6, # BEA Betaalautomaat 6
          'BIJ':  4, # BIJ Bijboeking 4
          'BTL':  4, # BTL Buitenlandse Overboeking 4
          'CHP':  6, # CHP Chipknip 6
          'CHQ':  2, # CHQ Cheque 2
          'ETC':  4, # ETC Euro traveller cheques 4
          'GBK':  4, # GBK GiroBetaalkaart 4
          'GEA':  3, # GEA Geldautomaat 3
          'INC': 11, # INC Incasso 11
          'IDB':  8, # IDB iDEAL betaling 8
          'IMB':  8, # IMB iDEAL betaling via mobiel 8
          'IOB':  4, # IOB Interne Overboeking 4 (niet 5: IOB is ook binnen zelfde bank naar andere klanten)
          'KAS':  3, # KAS Kas post 3
          'KTN': 10, # KTN Kosten/provisies 10
          'KST': 10, # KST Kosten/provisies 10
          'OVB':  4, # OVB Overboeking 4
          'PRM': 10, # PRM Premies 10
          'PRV': 10, # PRV Provisies 10
          'RNT': 10, # RNT Rente 10
          'TEL':  8, # TEL Telefonische Overboeking 8
          'VV':   4, # VV  Vreemde valuta 4
      }.get(x, 0)    # COR Correctie 0
                     # DIV Diversen 0
                     # EFF Effectenboeking 0
                     # STO Storno 0
      
def asn_parse(transactions):

    out = []
    errors = []
    currency = False
    
    for item in transactions:
        
        date = datetime.strptime(item[0],"%d-%m-%Y").strftime("%m/%d/%Y") # Boekingsdatum, converteren van DD-MM-YYYY naar MM/DD/YYYY
        
        paymode = asn_decode_paymentmode(item[14]) # Globale transactiecode
        
        info = item[14] # Globale transactiecode
        
        payee = ''.join(item[3].split("\n")) # Naam tegenrekening
        if item[3] != '':
            payee += ' ['+item[2]+']' # Tegenrekeningnummer
        
        desc = re.sub(' +', ' ', ''.join(item[17].split("\n"))) # Omschrijving (merge lines & remove multiple spaces)
        
        if (item[16] != ''):
            desk = ''.join(item[16].split("\n")) + desc # Betalingskenmerk
        
        amount = str(item[10]) # Transactiebedrag
        
        cat = ''
        
        tag = ''
        
        if currency == False:
            currency = item[7]
        if item[7] != currency or item[9] != currency: # different currencies in 1 file
            errors.append([item[0], item[9], amount, desc])
        
        out.append( [date, paymode, info, payee, desc, amount, cat, tag] )
        
        if len(errors) > 0:
            errormsg = "Foreign currencies were used in this ASN export file.\n\nBecause HomeBank does not accept different currencies in one import file, you need to import the following transaction(s) manually:\n\n"
            for e in errors:
                errormsg += ' '.join(e[:3])+"\n"+e[3]+"\n\n"
        else:
            errormsg = False

    return out,errormsg

############################################################################
#
# CSV loading
#
############################################################################

def cli_load_file(path):
    
    trans,errors,parser = load_file(path)
    
    if trans:
        
        msg = "Loaded '"+os.path.basename(path)+"'\n"+parser+', '+str(len(trans))+" rows"
        if len(trans) > 0:
            msg += ", from " + datetime.strptime(trans[0][0], "%m/%d/%Y").strftime("%d-%m-%Y") + " to " + datetime.strptime(trans[-1][0], "%m/%d/%Y").strftime("%d-%m-%Y")
        print(msg)
        
        if errors:
            print("Warning: "+errors)
        
        return trans
        
    else:
        print("Could not read '"+os.path.basename(path)+"':\nfile not supported or empty")
        return False

# Ask which file to load, load file, output info to GUI
def gui_load_file():
    
    global transactions
    
    path = tk.filedialog.askopenfilename()
    
    trans,errors,parser = load_file(path)
    
    if trans:
        
        transactions = trans
        
        btn_fileout.config(state="normal")
        
        msg = "Loaded '"+os.path.basename(path)+"'\n"+parser+', '+str(len(trans))+" rows"
        if len(transactions) > 0:
            msg += ", from " + datetime.strptime(trans[0][0], "%m/%d/%Y").strftime("%d-%m-%Y") + " to " + datetime.strptime(trans[-1][0], "%m/%d/%Y").strftime("%d-%m-%Y")
        status.config(text=msg)
        
        if errors:
            errwin = tk.Toplevel()
            errwin.title = "Warning"
            t = tk.Text(errwin, wrap="word")
            t.grid(row=1,column=1)
            t.insert(tk.INSERT,"Warning: "+errors)
            t.pack(fill="both")
            b = tk.Button(errwin, text="Close", width=10, command=errwin.destroy)
            b.pack()
            
            
    else:
        btn_fileout.config(state="disabled")
        status.config(text="Could not read '"+os.path.basename(path)+"':\nfile not supported or empty")

# Extract Homebank information from the CSV file at given path
# returns: transactions (list of list per transaction),
#          error messages as string,
#          used parser as string
def load_file(path):
    
    # try to open as ING CSV
    lengths,data = csv_as_list(open(path),',','\"')
    if lengths == [9]: # use row lengths to check for successful CSV reading
        transactions,errors,parser = ing_parse(data),[],'ING CSV'

    # try to open as ASN CSV
    elif lengths == [19]:
        lengths,data = csv_as_list(open(path),',','\'') # CSV
        if lengths == [19]:
            (transactions,errors),parser = asn_parse(data),'ASN CSV'
    elif lengths == [1]:
        lengths,data = csv_as_list(open(path),';','\"') # CSV 2004
        if lengths == [19]:
            (transactions,errors),parser = asn_parse(data),'ASN CSV 2004'

    # not able to open
    if not 'transactions' in vars() or transactions is False:
        return False,False,False
    
    return transactions,errors,parser


# Read CSV from string
# returns: list of unique field lengths per line in CSV,
#          list of list of fields per line in CSV
def csv_as_list(strdata,delimiter=',',quotechar='\"'):
    csvdata = csv.reader(strdata,delimiter=delimiter,quotechar=quotechar)
    data = []
    try:
        for row in csvdata:
            data.append(row)
    except:
        pass
    lengths = list(set([len(x) for x in data]))
    return lengths,data # lengths: list of unique row lengths, data: list of transactions


############################################################################
#
# CSV saving
#
############################################################################

def save_file(path):
    with open(path, 'w', newline='') as csvfile:
        hbwriter = csv.writer(csvfile, delimiter=';', quotechar='\"', quoting=csv.QUOTE_MINIMAL)
        for t in transactions:
            # date ; payment mode ; info ; payee ; memo ; amount ; category ; tags
            hbwriter.writerow(t)

def gui_save_file():
    path = tk.filedialog.asksaveasfile(mode='w', defaultextension=".csv").name
    save_file(path)
    status.config(text="Written to "+os.path.basename(path))

def gui_menu_save_file():
    if btn_fileout.cget("state") == "disabled":
        tk.messagebox.showerror("Save","Nothing to save, load a file first!")
    else:
        gui_save_file()


############################################################################
#
# CLI routine
#
############################################################################

if len(sys.argv) != 1:

    print("\nHomeBank CSV Converter for ASN and ING")
    print("Copyright 2019 Caspar Verhey\n")
    
    if len(sys.argv) != 3:
    
        print("CLI usage:\n\n\t"+sys.argv[0]+" <input CSV> <output CSV>\n")
        print("More information: https://github.com/cwverhey/HomeBankCSV\n")
    
    else:
    
        transactions = cli_load_file(sys.argv[1])
        if transactions:
            save_file(sys.argv[2])
    
else:

############################################################################
#
# GUI routine
#
############################################################################

    def show_about():
        tk.messagebox.showinfo("About","HomeBank CSV Converter v. "+version+"\n\nConverts Dutch ING Bank and ASN Bank CSV files to a format the HomeBank software (http://homebank.free.fr) understands.\n\nhttps://github.com/cwverhey/homebankcsv")

    def show_website():
        webbrowser.open_new_tab('https://github.com/cwverhey/HomeBankCSV')

    # storage for transaction info between writing and reading
    transactions = []

    # create GUI window
    win = tk.Tk()
    win.title("HomeBank CSV Converter")

    # raise
    win.lift()
    win.attributes('-topmost',True)
    win.after_idle(win.attributes,'-topmost',False)

    # determine accelerator / key bindings
    if platform.system() == "Darwin":
        acc_load = 'Command-o'
        acc_save = 'Command-s'
        win.bind_all("<Command-o>", lambda event: win.after(200,gui_load_file)) # workaround for MacOS
        win.bind_all("<Command-s>", lambda event: win.after(200,gui_save_file))
    else:
        acc_load = 'Control-o'
        acc_save = 'Control-s'

    # add menu bar
    menu = tk.Menu(win)
    filemenu = tk.Menu(menu, tearoff=0)
    filemenu.add_command(label='Load...', command=gui_load_file, accelerator=acc_load)
    filemenu.add_command(label='Save...', command=gui_menu_save_file, accelerator=acc_save)
    filemenu.add_separator() 
    filemenu.add_command(label='Quit', command=win.quit)
    menu.add_cascade(label='File', menu=filemenu) 
    helpmenu = tk.Menu(menu, tearoff=0) 
    helpmenu.add_command(label='About', command=show_about)
    helpmenu.add_command(label='Visit website', command=show_website)
    menu.add_cascade(label='Info', menu=helpmenu)
    win.config(menu=menu)

    # add logo
    logo_gif = tk.PhotoImage(data='''
    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
    ''') # base64 gif w/ transparency
    logo = tk.Label(win, image=logo_gif)
    logo.pack(padx=20,pady=10)

    # add buttons and status label
    btn_filein = tk.Button(win, text="Load bank export CSV file...", width=25, command=gui_load_file)
    btn_filein.pack(padx=10,pady=0)

    status = tk.Label(win, text="")
    status.pack(padx=10,pady=0)

    btn_fileout = tk.Button(win, state="disabled", text="Save as HomeBank CSV file...", width=25, command=gui_save_file)
    btn_fileout.pack(padx=10,pady=10)

    btn_quit = tk.Button(win, text="Quit", width=10, command=win.quit)
    btn_quit.pack(padx=10,pady=10)

    # run loop
    win.mainloop()