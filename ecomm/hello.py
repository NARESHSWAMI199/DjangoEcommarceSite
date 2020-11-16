import smtplib

try:
   ''' here we sending a mail to user about order '''
   ob = smtplib.SMTP('smtp.gmail.com',587)
   
   ''' encript connection using  "tls"  using a stmp class fuction  '''
   ob.starttls() 
   
   ''' login using our gmail for stmp '''
   ob.login('swaminaresh993@gmail.com',"$w@m!**boy#..123")

   ''' subject '''
   subject  = "Order Successfull on Nsfuntu"
   ''' body '''
   body = "your order is successfully you will recive today 12:on clock and your ref id is "


   ''' create message using format method '''
   message = "Subject : {} /n /n {}".format(subject,body)

   sender = 'swaminaresh993@gmail.com'
   reciver = ['nareshswami2334@gmail.com']

   ob.sendmail(sender,reciver,message)
   ob.quit()
   ''' if success '''
   print("successfully send")
except: 
   print("successfully not send")