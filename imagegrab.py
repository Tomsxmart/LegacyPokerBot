import numpy as np
import cv2
from mss import mss
from PIL import Image
import time
import glob
import os
import pytesseract
from game_logic import evaluation
mon = {'top': 25, 'left': 0, 'width': 1920, 'height': 1010}
if (os.name=='nt'):
    pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'

## cheat sheet
#karavs -dimants
#ercens - sirds
#kreicis - lapa
#pikis - melna sirds
    
templatearr=glob.glob('./images/*.jpg')

# how accurate will it match images (1 highest 0 lowest)
threshold =0.9

def card_rating(card):
    if(card=='1'):
        return 1
    elif(card=='2'):
        return 2
    elif(card=='3'):
        return 3
    elif(card=='4'):
        return 4
    elif(card=='5'):
        return 5
    elif(card=='6'):
        return 6
    elif(card=='7'):
        return 7
    elif(card=='8'):
        return 8
    elif(card=='9'):
        return 9
    elif(card=='10'):
        return 10
    elif(card=='j'):
        return 11
    elif(card=='q'):
        return 12
    elif(card=='k'):
        return 13
    else:
        return 14

def recognise_card(stream,threshold,stream_gray):
    test=0
    test2=1
    test3=1;
    doonce=True
    hand={}
    table={}
    history=[]
    points=[]
    response={}
    tableinfo=[]
    historycheck=False
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    for singletemplate in templatearr: #loops through all image names
        test=test+1
        count = 0;
        doonce=True
        
        template = cv2.imread(singletemplate,0) #reads the image
        w,h = template.shape[::-1] #dimensions of the image
        res = cv2.matchTemplate(stream_gray,template,cv2.TM_CCOEFF_NORMED) # matches
        loc = np.where(res >= threshold)
        cv2.putText(stream,'Hand',(0,50),font,1,(255,255,0),2,cv2.LINE_AA)
        cv2.putText(stream,'Table',(800,50),font,1,(255,255,0),2,cv2.LINE_AA)

        for pt in zip(*loc[::-1]):
            count=count+1 #rating system, how confident the ai is(pretty shitty ik)

            if (pt[1]<350 and pt[1] >100): # might change on real client (the position of identified card )
                if(doonce):
                    points='table' # check if the position of identified card is above hand or not
                    doonce=False
            else:
                if(doonce):
                    if(pt[1]>350):
                        points='hand'
                        doonce=False

            cv2.rectangle(stream,pt,(pt[0]+w,pt[1]+h),(0,255,255),1)#draws around the item ai is confident about

        if os.name == 'nt':
            singletemplate=singletemplate.split('\\')[1]
            singletemplate=singletemplate.split('.')[0]

        else:    
            singletemplate=singletemplate.split('/')[2] #remove unnecesary string parts from cardname
            singletemplate=singletemplate.split('.')[0]

        if(points=='hand' and count > 0):
            cv2.putText(stream,singletemplate,(0,100+test3*50), font, 1,(0,255,0),2,cv2.LINE_AA) #labels the item
            test3=test3+1

        if(points=='table' and count > 0): 
            cv2.putText(stream,singletemplate,(800,100+test2*50), font, 1,(0,255,0),2,cv2.LINE_AA) #labels the item
            test2=test2+1

        history.extend([count]) #history for remembering if any items were found

        for historyelement in history: #checks if all history elements confidence is 0 then clears the hand and table (new cards)
            if (historyelement>0):
                historycheck=False
                break   

            historycheck=True
                
        if(test==len(templatearr) and historycheck): # continuines checking history elements
                response={};
                hand={};
                table={}

        if not response: 
            response['count']=count
        else:

            if(count>response['count']): #if more confidence than another card replaces it (avoid false positives)
                response['count']=count

        if(count>0):
            card =singletemplate.split('_')

            if(points=='hand'):
                hand[card[1]]=[{'card':card[1],'type':card[0], 'rating':card_rating(card[1])}]
            else:
                if(points=='table'):
                    table[card[1]]=[{'card':card[1],'type':card[0], 'rating':card_rating(card[1])}]

    tableinfo.append([table])
    tableinfo.append([hand])

    if(response['count']<=0):
        return 'no cards were found!'
    else:
        return tableinfo
        
def process_img(original_image):
    processed_img=cv2.cvtColor(original_image,cv2.COLOR_BGR2GRAY)
    return processed_img

def game_logic_check(table,hand,money):
    allcards=[]

    for tablecards,tablekey in table.items():
        tablekey[0]['origin']='table'
        allcards.append([tablekey[0]])

    for handcards,handkey in hand.items():
        handkey[0]['origin']='hand'
        allcards.append([handkey[0]])
    #goes to game_logic and rating evaluation/combination recognition
    risk=evaluation(allcards)
    #TODO:read cash 
    #TODO: pass the data to game_controller logic with risk level and money
    
def track_image():
    last_time = time.time()
    sct = mss()
    sct.get_pixels(mon) #gets image
  
    img = Image.frombytes('RGB', (sct.width, sct.height), sct.image)
    new_img=process_img(np.array(img)) 
    b, g, r = img.split()
    img=Image.merge("RGB",(r,g,b)) #split the color channels to make rgb out of bgr

    img_bgr = np.array(img)
    crop_img = img_bgr[425:460, 400:470] #change to client needs (reads your cash)
    cash = pytesseract.image_to_string(crop_img,config='outputbase digits')
    
    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    response=recognise_card(img_bgr,threshold,img_gray)
    #TODO:remove this when have detection when its your turn

    if not response=='no cards were found!':
        print('trigger')
        game_logic_check(response[0][0],response[1][0],cash)
    else:
        print('no cards were found!')
    cv2.imshow('detected', np.array(img_bgr)) # shows the image
        
    last_time=time.time()

    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        

track_image()

