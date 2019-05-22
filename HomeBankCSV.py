#!/usr/bin/env python3

# TODO:
# * remember input dir & output dir
# * Windows: icoon in taakbalk & venster
# * Windows: Installer icoon
# * Mac: About overnemen
# * Mac: quit verbergen
# * Mac: Info-menubalk in globale bar verwerken
# * 1e argument in GUI-mode direct inlezen
# * CLI mode netjes inpassen

import csv
from   datetime import datetime
import os
import platform
import re
import sys
import tkinter as tk
from   tkinter import filedialog, messagebox
import webbrowser

version = "201905220"

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
        if item[5] == "Af": # Af/Bij
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
        if item[2] != '':
            payee += ' ['+item[2]+']' # Tegenrekeningnummer
        
        desc = re.sub(' +', ' ', ''.join(item[17].split("\n"))) # Omschrijving (merge lines & remove multiple spaces)
        if (item[16] != ''):
            desc += ''.join(item[16].split("\n")) + desc # Betalingskenmerk
        
        amount = str(item[10]) # Transactiebedrag
        
        cat = ''
        
        tag = ''
        
        if item[7] != 'EUR' or item[9] != 'EUR': # different currencies in 1 file
            errors.append([item[0], item[9], amount, desc])
        
        out.append( [date, paymode, info, payee, desc, amount, cat, tag] )
        
        if len(errors) > 0:
            errormsg = "Currencies other than EUR were found in this ASN export file. Because HomeBank does not accept different currencies in one import file, verify the following transaction(s) manually after importing:\n\n"
            for e in errors:
                errormsg += ' '.join(e[:3])+"\n"+e[3]+"\n\n"
        else:
            errormsg = False

    return out,errormsg

############################################################################
#
# Triodos (codes derived from https://github.com/akretion/banking/blob/master/account_banking_nl_triodos/triodos.py)
#
############################################################################

def triodos_decode_paymentmode(x):
      return {
          'AC':   4, # Acceptgiro gecodeerd
          'AN':   4, # Acceptgiro ongecodeerd
          'AT':   8, # Acceptgiro via internet
          'BA':   6, # Betaalautomaat
          'CHIP': 3, # Chipknip
          'CO':  10, # Correctie
          'DB':   8, # Diskettebetaling
          'DV':  10, # Dividend
          'EI':  11, # Europese Incasso
          'EICO': 11, # Europese Incasso Correctie
          'EIST': 11, # Europese Incasso Storno
          'ET':   4, # Europese Transactie
          'ETST': 4, # Europese Transactie Storno
          'GA':   3, # Geldautomaat
          'IB':   5, # Interne Boeking
          'IC':  11, # Incasso
          'ID':   8, # iDeal-betaling
          'IT':   8, # Internet transactie
          'KN':  10, # Kosten
          'KO':   3, # Kasopname
          'KS':  10, # Kwaliteitsstoring
          'OV':   4, # Overboeking. NB: can also be 10 when no remote account specified!
          'PO':   7, # Periodieke Overboeking
          'PR':  10, # Provisie
          'RE':  10, # Rente
          'RS':  10, # Renteschenking
          'ST':   4, # Storno
          'TG':   8, # Telegiro
          'VL':  11, # Vaste Lening
          'VO':  11, # Vordering overheid
          'VV':   4, # Vreemde valuta
      }.get(x, 0)
      
def triodos_parse(transactions):

    out = []
    for item in transactions:
        
        date = datetime.strptime(item[0],"%d-%m-%Y").strftime("%m/%d/%Y") # Boekingsdatum, converteren van DD-MM-YYYY naar MM/DD/YYYY
        
        paymode = triodos_decode_paymentmode(item[6]) # transactietype
        
        info = item[6] # transactietype
        
        payee = item[4] # tegenrekening
        if item[5] != '':
            payee += ' ['+item[5]+']' # Tegenrekeningnummer
        
        desc = re.sub(' +', ' ', ''.join(item[7].split("\n"))) # Omschrijving (merge lines & remove multiple spaces)

        amount = str(item[2]) # Transactiebedrag
        if item[3] == 'Debet':
            amount = '-'+amount
        
        cat = ''
        
        tag = ''
        
        out.append( [date, paymode, info, payee, desc, amount, cat, tag] )

    return out

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
    if path == '':
        return False
        
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
            transactions,errors,parser = asn_parse(data) + ('ASN CSV',)
    elif lengths == [1]:
        lengths,data = csv_as_list(open(path),';','\"') # CSV 2004
        if lengths == [19]:
            transactions,errors,parser = asn_parse(data) + ('ASN CSV 2004',)
            
    # try to open as Triodos CSV
    elif lengths == [8]:
        transactions,errors,parser = triodos_parse(data),[],'Triodos CSV'

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
    try:
        path = tk.filedialog.asksaveasfile(mode='w', defaultextension=".csv").name
    except:
        return False
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

    print("\nHomeBank CSV Converter for ASN, ING and Triodos Bank (NL)")
    print("Copyright 2019 Caspar Verhey\n")
    
    if len(sys.argv) != 3:
    
        print("CLI usage:\n\n\t"+sys.argv[0]+" <input CSV> <output CSV>\n")
        print("More information: https://github.com/cwverhey/HomeBankCSV\n")
    
    else:
    
        transactions = cli_load_file(sys.argv[1])
        if transactions:
            save_file(sys.argv[2])
            print("Written to '"+os.path.basename(sys.argv[2])+"'")
    
else:

############################################################################
#
# GUI routine
#
############################################################################

    def show_about():
        tk.messagebox.showinfo("About","HomeBank CSV Converter v. "+version+"\n\nConverts Dutch ASN, ING and Triodos Bank CSV files to a format the HomeBank software (http://homebank.free.fr) understands.\n\nhttps://github.com/cwverhey/homebankcsv")

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
        acc_load = 'Ctrl-o'
        acc_save = 'Ctrl-s'

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