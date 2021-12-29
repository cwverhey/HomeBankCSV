# HomeBank CSV Converter for ASN, ING & Triodos Bank 🇳🇱

If you use the [HomeBank](http://homebank.free.fr/en/index.php) accounting software, you'll probably want to import transaction data from your bank into HomeBank. I made a tool to convert Dutch ING Bank, ASN Bank and Triodos Bank comma-separated (CSV) downloads to a CSV file that HomeBank will understand.

This software is available as Python script and as standalone executables for Windows and MacOS.
 
## Version info

Latest version: 22 may 2019, added Triodos Bank NL, fixed ING debit/credit bug.

Known bugs/imperfections:
- if you open the file select dialog on Windows and press cancel, you'll receive a warning message as soon as you quit the program; feel free to ignore that warning;
- it's not yet possible to drag-and-drop files to the program.

Check back here if you ever need updates, contact me (bottom of this page) if you're having any trouble. I don't want to add an automatic check for updates; to avoid causing any concerns over your privacy this app would better not phone home.

## MacOS .app
Download [HomeBankCSV.app.zip](https://github.com/cwverhey/HomeBankCSV/raw/master/releases/HomeBankCSV.app.zip) and unzip. Run the HomeBankCSV.app. To install, drag it to your Applications folder.

Installing Python is not necessary: the required files are included in the app.

<img align="left" src="build-files/images/screenshot_macos.png" />
<br clear="all" />

## Windows .exe
Download [HomeBankCSVInstaller.exe](https://github.com/cwverhey/HomeBankCSV/raw/master/releases/HomeBankCSVInstaller.exe) and run this installer. It will unpack the required files to a directory you choose, and if you want it will also create a start menu shortcut. Uninstall any old versions before installing this one.

If you don't want to install, download [HomeBankCSV.exe](https://github.com/cwverhey/HomeBankCSV/raw/master/releases/HomeBankCSV.exe).

<img align="left" src="build-files/images/screenshot_windows.png" />
<br clear="all" />

## Linux & power users
Grab HomeBankCSV.py and run it, just make sure you have Python 3.6+ installed.

### CLI
    chmod +x HomeBankCSV.py
	./HomeBankCSV.py <input file> <output file>

- Input file: ING/ASN CSV
- Output file: CSV for HomeBank Import, for CLI this will overwrite any existing file with the same name

### GUI
    chmod +x HomeBankCSV.py
	HomeBankCSV.py

Start without arguments to launch the GUI.

## More information
### HomeBank CSV format
Column list:

    date ; payment mode ; info ; payee ; memo ; amount ; category ; tags

```
date     => Specifications claim DD-MM-YY, but that didn't work for me; HB seems to expect MM/DD/YYYY instead
payment mode  => 0 = None; 1 = Credit Card; 2 = Check; 3 = Cash; 4 = Transfer; 5 = Internal Transfer; 6 = Debit Card; 7 = Standing Order; 8 = Electronic Payment; 9 = Deposit; 10 = Financial Institutions fee (transaction fees etc.); 11 = Direct Debit
info     => a string
payee    => a payee name
memo     => a string
amount   => a number with a '.' or ',' as decimal separator, eg: -24.12 or 36,75
category => a full category name (category, or category:subcategory) eg: insurance:healthcare or groceries 
tags	 => tags separated by space (mandatory since HomeBank v4.5)
```

#### Example
    15-02-04;0;;;ATM cash withdrawal;-40,00;Bill:Withdrawal of cash;tag1
    15-02-04;1;;;Internet DSL;-45,00;Inline service/Internet;tag2
    ...

### Contact info
Feel free to mail me: caspar@verhey.net. Ik spreek ook Nederlands ;)
