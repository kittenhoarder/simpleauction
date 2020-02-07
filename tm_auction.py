#Helps convert into correct types
import json

def typeConverter(l):
    for i in l:
        try:
            yield json.loads(i)
        except ValueError:
            yield i

# Read in input.txt as a string
readInput = open('input.txt')
stringInput = readInput.read()
readInput.close() 

#Split out string and make it a list
stringInput = stringInput.replace('\n', '|\n|')
listInput = stringInput.split('|')
listInput = list(typeConverter(listInput))
if listInput[1] == '\n': #help identify possible initial heartbeat object later
  listinput = listInput.insert(0,'\n')

#input: cursor (is listInput index of bid object 'item')
def updateStats(cursor):
  global listInput, auctionList, bidList, invalidBidList
  tempBidPriceList = []
  tempStatsList = []
  # Iterate over bid objects, collect corresponding item bidprices in tempStatsList
  i=0
  while i < len(bidList):
    if bidList[i+3] == listInput[cursor+1]:
      tempBidPriceList.append(bidList[i+4]) # add correct bid prices tempStatsList
      i+=6
    else:
      i+=6
  #Write stats
  if auctionList[auctionList.index(listInput[cursor+1])] in bidList: #if previous bids
    auctionList[auctionList.index(listInput[cursor+1])+4] = 'SOLD'  # status
    if len(tempBidPriceList) >= 2:                     #if 2+ bids then get second highest, else get, bidprice and append it as
      auctionList[auctionList.index(listInput[cursor+1])+5] = "{0:0.2f}".format(tempBidPriceList[-2]) #price_paid
      auctionList[auctionList.index(listInput[cursor+1])+3] = bidList[len(bidList)-bidList[::-1].index(listInput[cursor+1])+1-4] #add bidwinner
    if len(tempBidPriceList) == 1:
      auctionList[auctionList.index(listInput[cursor+1])+5] = "{0:0.2f}".format(auctionList[auctionList.index(listInput[cursor+1])+1]) #price_paid

    auctionList[auctionList.index(listInput[cursor+1])+3] = bidList[len(bidList)-bidList[::-1].index(listInput[cursor+1])+1-4] #add bidwinner
  auctionList[auctionList.index(listInput[cursor+1])+6] = len(tempBidPriceList) # total
  
  # Iterate over bid objects in invalidBidList, collect corresponding item bidprices in tempStatsList for hi low only
  i=0 
  while i < len(invalidBidList):
    if invalidBidList[i+3] == listInput[cursor+1]:
      tempBidPriceList.append(invalidBidList[i+4])   # add correct bid prices tempStatsList
      i+=6
    else:
      i+=6
  auctionList[auctionList.index(listInput[cursor+1])+7] = "{0:0.2f}".format(max(tempBidPriceList)) # hi
  auctionList[auctionList.index(listInput[cursor+1])+8] = "{0:0.2f}".format(min(tempBidPriceList)) # low

def auctionCloser(inputObj): #inputs current time from listInput object being processed in main method
  global auctionList, time
  z = 0
  while z < len(auctionList):
    if auctionList[z+2] == 'SELL' and time == auctionList[z+5]:
      processToOutput(z) # Send auction index # to processToOutput
    z+=13
def processToOutput(i): # input sold or unsold auction index from auctionList
  global auctionList
  tempList = []
  outputString = ''
  tempList.append(auctionList[i+5])
  tempList.append(auctionList[i+3])
  tempList.append(auctionList[i+6])
  tempList.append(auctionList[i+7])
  tempList.append(auctionList[i+8])
  tempList.append(auctionList[i+9])
  tempList.append(auctionList[i+10])
  tempList.append(auctionList[i+11])

  q = 0
  while q < len(tempList):
    outputString += str(tempList[q])
    if q < len(tempList)-1:
      outputString += '|'
    else:
      break
    q += 1
  print(outputString)

#Main Method
#import pdb; pdb.set_trace()  
time = x = 0 #tested
auctionList = []
bidList = [] 
invalidBidList = []
outputString = ''

while x < len(listInput):
  #If heartbeat, check time and then run auctionCloser
  if listInput[x] == '' and listInput[x-1] == '\n': #end of input file
    break
  if listInput[x-1] == '\n' and listInput[x+1] == '\n': #if heartbeat is first item in list
    time = listInput[x]
    auctionCloser(listInput[x])

  #if auction, update time, then add auction to auctionList, run auction closer
  elif listInput[x] == 'SELL':
    time = listInput[x-2]
    auctionList.extend(listInput[x-2:x+4])       #add auction to auctionList
    auctionList.append('')
    auctionList.append('UNSOLD')
    auctionList.append(0) #add unsold stats to auction in auctionList
    auctionList.append(0)
    auctionList.append(0.00) 
    auctionList.append(0.00)
    auctionList.append('\n')
    auctionCloser(listInput[x-2])

  elif listInput[x] == 'BID': #TO DO: test this(x)
    time = listInput[x-2] 
    #check if arrives after auction start time and before closing and doesnt meet reservePrice
    if listInput[x-2] < auctionList[auctionList.index(listInput[x+1])+2]: #close time OK
      if listInput[x-2] > auctionList[auctionList.index(listInput[x+1])-3]: #start time OK
        if listInput[x+1] not in bidList:  # If bidList doesnt have a item bid
          if listInput[x+2] >= auctionList[auctionList.index(listInput[x+1])+1]: #if bid meets/exceeds reserve:
            bidList.extend(listInput[x-2:x+4]) #add bid to end bidList, include end '\n'
            updateStats(x)
            auctionCloser(listInput[x-2])
          else:
            invalidBidList.extend(listInput[x-2:x+4])
            auctionCloser(listInput[x-2])

        elif listInput[x+1] in bidList:         # If bidList has a item bid
          if listInput[x+2] > bidList[len(bidList)-bidList[::-1].index(listInput[x+1])+1-1]: #if bid exceeds previous bid
            bidList.extend(listInput[x-2:x+4]) #add bid to end bidList, include end '\n'
            updateStats(x) #Update auction Stats using bidlist as source
            auctionCloser(listInput[x-2])
          #if bid is the same as previous largest bid insert it in the previous large bids place
          elif listInput[x+2] == bidList[len(bidList)-bidList[::-1].index(listInput[x+1])+1-1]:
            bidList.insert(-6,listInput[x-2])
            bidList.insert(-6,listInput[x-1])
            bidList.insert(-6,listInput[x])
            bidList.insert(-6,listInput[x+1])
            bidList.insert(-6,listInput[x+2])
            bidList.insert(-6,listInput[x+3])
            updateStats(x) #Update auction Stats using bidlist as source
            auctionCloser(listInput[x-2])
          else:
            invalidBidList.extend(listInput[x-2:x+4])
            auctionCloser(listInput[x-2])

      else:
        invalidBidList.extend(listInput[x-2:x+4])
        auctionCloser(listInput[x-2])
    else:
      invalidBidList.extend(listInput[x-2:x+4])
      auctionCloser(listInput[x-2])
    auctionCloser(listInput[x-2])
  x+=1