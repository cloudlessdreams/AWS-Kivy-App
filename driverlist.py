import csv
import boto3

### this takes a list of usernames (in this case drivers) and their pins (passwords
### and passes it through the initial AWS auth flow to change their pins to their existed
### Autocab pins.

def listdrivers():

    ## this is just a test function
    with open('Driver2019.csv', 'r') as f:
      reader = csv.reader(f)
      your_list = list(reader)

    for i in your_list:
        print(i[1])


### second test function

dlist = ['41', '32']
plist = ['1234','1234','1234','1234']

def driverslist():
    global dlist
    if len(dlist) > 0:
        print(dlist[0])
        del dlist[0:]

## this is testing the pins

def pins():
    global plist
    if len(plist) > 0:
        print(str(plist[0]) + str(plist[0]))
        del plist[0:]

def finalfunc():
    global dlist
    global plist

    user = dlist[0]
    passw = plist[0]

    ## this pin is 4 digits so this concats them to create the min 8 char len
    pin = passw + passw

    if len(dlist) > 0:
        for i in dlist:
            ## this loop passes each user name through the AWS client
            client = boto3.client('cognito-idp')
            response = client.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': user,

                    # all the default passwords were Password123
                    'PASSWORD': 'Password123'
                },
                ## this must be unique to each cognito pool
                ClientId='597l56b7t423luu70ur/home/ajmaljsrq9f7'
            )
            sess = response['Session']

            tokens = client.respond_to_auth_challenge(
                ## same as above
                ClientId='597l56b7t423luu70urjsrq9f7',
                ChallengeName='NEW_PASSWORD_REQUIRED',
                Session=sess,
                ChallengeResponses={
                    'NEW_PASSWORD': pin,
                    'USERNAME': user
                }
            )
            del dlist[:0]
        print(dlist)
finalfunc()
