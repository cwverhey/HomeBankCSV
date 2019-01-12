### HomeBank CSV format
Column list:
date ; payment mode ; info ; payee ; memo ; amount ; category ; tags

Values:
'''
date     => (NOTE: didn't work according to spec, HB seems to expect MM/DD/YYYY) format should be DD-MM-YY
payment mode  => 0 = None; 1 = Credit Card; 2 = Check; 3 = Cash; 4 = Transfer; 5 = Internal Transfer; 6 = Debit Card; 7 = Standing Order; 8 = Electronic Payment; 9 = Deposit; 10 = Financial Institutions fee (transaction fees etc.); 11 = Direct Debit
info     => a string
payee    => a payee name
memo     => a string
amount   => a number with a '.' or ',' as decimal separator, ex: -24.12 or 36,75
category => a full category name (category, or category:subcategory)
tags	 => tags separated by space (mandatory since HomeBank v4.5)
'''
#### Example
15-02-04;0;;;Some cash;-40,00;Bill:Withdrawal of cash;tag1
15-02-04;1;;;Internet DSL;-45,00;Inline service/Internet;tag2
...