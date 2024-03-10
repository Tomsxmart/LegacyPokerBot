from collections import Counter
import operator
import numpy as np
import os
from operator import itemgetter
risk=10; #hardcoded risk level managment
def evaluate_flush(cards,cardtype,count):
    #for card in cards:
    tableamount=0
    handamount=0
    for card in cards:
        #print(card['origin'])
        if card['origin']=='table':
            tableamount=tableamount+1
        else:
            handamount=handamount+1
    print(tableamount)
    print(handamount)
def check_flush(cards):
    karavs_count=0
    karavs_cards=[]
    pikis_count=0
    pikis_cards=[]
    kreicis_count=0
    kreicis_cards=[]
    ercens_count=0
    ercens_cards=[]
    for card in cards:
        ## will be remade in the future
        karavs=Counter(card[0].values())['karavs']
        if karavs==1:
            karavs_cards.extend(card)
            karavs_count=karavs_count+1
            
            #evaluate_flush(karavs_cards,'karavs',karavs_count) # checks if it is getting near a flush
            if karavs_count >=5:
                temprating=0
                for karavs_card in karavs_cards:
                    if temprating < karavs_card['rating']:
                        temprating=karavs_card['rating']
                return temprating
            
        pikis=Counter(card[0].values())['pikis']
        if pikis==1:
            pikis_cards.extend(card)
            pikis_count=pikis_count+1
            if pikis_count >=5:
                temprating=0
                for pikis_card in pikis_cards:
                    if temprating < pikis_card['rating']:
                        temprating=pikis_card['rating']
                return temprating
        
        kreicis=Counter(card[0].values())['kreicis']
        if kreicis==1:
            kreicis_cards.extend(card)
            kreicis_count=kreicis_count+1
            if kreicis_count >=5:
                temprating=0
                for kreicis_card in kreicis_cards:
                    if temprating < kreicis_card['rating']:
                        temprating=kreicis_card['rating']
                return temprating
        
        ercens=Counter(card[0].values())['ercens']
        if ercens==1:
            ercens_cards.extend(card)
            ercens_count=ercens_count+1
            if ercens_count >=5:
                temprating=0
                for ercens_card in ercens_cards:
                    if temprating < ercens_card['rating']:
                        temprating=ercens_card['rating']
                return temprating
       
    return None

def check_pair(cards):
    pair=[]
    card_ratings=[1,2,3,4,5,6,7,8,9,10,11,12,13,14]
    for rating in card_ratings:
        occurence=0;
        origin=[]
        for card in cards:
            value_occurences=Counter(card[0].values())[rating]
            if value_occurences==1:
                occurence=occurence+1
                origin.extend([{'origin':card[0]['origin'],rating:rating}])
        if occurence >=2:
            pair.extend([{'pairamount':occurence,'cards':origin}])
            
    if not pair:
        return None
    
    return pair

def check_straight(cards):
    ratinglist=[]
    ratingsonly=[]
    for card in cards:
        
        childlist=[]
        ratinglist.append([card[0]['rating']])
        key=find_element_in_list([card[0]['rating']],ratinglist)
        ratingsonly.extend([card[0]['rating']])
        childlist.extend([card[0]['rating'],[card[0]['origin']]]) # get the format of data to be sorted
        ratinglist[key]=childlist
    
    ratinglist=sorted(ratinglist)
    ratingsonly=sorted(ratingsonly) # make same list to remember the key of the array
    response=[]
    straightcards=[]
    for rating in ratinglist:
        i=0;
        count=0
        cards=[]
        while i<=5:
            
            iterator=rating[0]+i # make same array without overriding it
            if iterator in ratingsonly:
                count=count+1
                cards.extend([iterator])
                if count ==5:
                    straightcards=cards
            else:
                break;
            
            i=i+1
    if not straightcards:
        return None
    else:
        tablecards=[]
        handcards=[]
        for straightcard in straightcards: #find if the card is on table or hand (for risk level)
            if find_element_in_list([straightcard,['hand']],ratinglist) == None:
                tablecards.extend([straightcard])
            else:
                handcards.extend([straightcard])
        if max(tablecards) > max(handcards):
            return 'highest table'
        else:
            return 'highest hand'
        
def find_element_in_list(element, list_element):
    try:
        index_element = list_element.index(element)
        return index_element
    except ValueError:
        return None
    
def check_fullhouse(pairs):
    pairamount=0
    for pair in pairs:
        pairamount=pairamount+pair['pairamount']
    if pairamount == 5:
        return 'fullhouse'
    else:
        return None
    
def evaluate_table_flush(cards):
    global risk
    tablecards=[]
    for card in cards: ##get only table cards
        if card[0]['origin']=='table':
            tablecards.append(card[0])
    tableamount=len(tablecards)
    cardtypes=['ercens','karavs','kreicis','pikis']
    doonce=True
    doonce1=True
    doonce2=True ## dunno how to else avoid repeating loops
    for cardtype in cardtypes:
        typecount=0;
        iterationcount=0;
        for card in tablecards:#loops through table cards to check for types combo
            counter=Counter(card.values())[cardtype]
            iterationcount=iterationcount+1
            if counter==1:
                typecount=typecount+1
                if len(tablecards)==iterationcount:
                    if tableamount<5 and tableamount >=3:
                        if typecount ==2: ## check if its approaching for a possibility of a flush
                            if doonce2:
                                print('POSSIBILITY:small possiblity of flush for',cardtype)
                                risk=risk-1
                                doonce2=False
                    if typecount ==3:
                        if doonce:
                            
                            print('POSSIBILITY:possible flush of',cardtype)
                            risk=risk+4 ## if there are 3 types on the table theres a possible flush
                            doonce=False ## prevents from duplicate risk adds
                    if typecount >=4: ## if there is 4 types on the table
                        if doonce1:
                            print('POSSIBILITY:big possiblity of flush for',cardtype)
                            risk=risk+8
                            doonce1=False

def evaluate_pair(pair,cards):
    global risk
    if pair[0]['cards'][1]['origin']=='table' and pair[0]['cards'][0]['origin']=='table':
        risk=risk+2
        print('IGNORED:table pair, ignored')
    else:
        cardratings=[]
        for card in cards:
            cardratings.extend([card[0]['rating']]) # checks if the pair is the highest from table
        paircard=pair[0]['cards'][0].keys()
        paircard=list(paircard)
        paircard=[e for e in paircard if isinstance(e, int)][0] #stackoverflow filter integer out of list(sometimes it was in index 1 sometines on index 0
        if paircard==max(cardratings):
            print('COMBO:highest pair on table')
            risk=risk-4
        
def rating_system(highest,combo,cards):
    #will add more factors in the future, for now just want to get it working
    global risk
    if combo=='pair':
        #evaluates if highest pair and if count is 2 or 3 or 4
        if highest[0]['pairamount'] ==3:
            print('COMBO:pair of 3!')
            risk=risk-6
        elif highest[0]['pairamount'] ==4:
            print('COMBO:pair of 4!')
            risk=risk-10
        else:
            if(len(highest)==2): #stops 2 pairs from overriding pair of 4
                print('COMBO:pair of 4!')
                risk=risk-10
            else:
                print('COMBO:pair of 2!')
                
                risk=risk-2
                evaluate_pair(highest,cards)
        
    if combo=='two pair':
        print('COMBO:two pairs!')
        risk=risk-4
        # evaluates if there is highest pair in hand
        evaluate_pair([highest[0]],cards)
        evaluate_pair([highest[1]],cards)
    if combo=='straight':
        
        if highest=='highest hand':
            risk=risk-10
            #checks if there is no flush so it can be 0 risk
            print('COMBO:straight high hand!')
        else:
            risk=risk-4
            print('COMBO:straight high table!')
    if combo=='flush':
        print('COMBO:flush')
        risk=risk-7
        #TODO:evaluate if you have highest flush
    if combo=='fullhouse':
        print('COMBO:fullhouse')
        risk=risk-10
        #TODO:evaluate if you have possible the highest fullhouse

def evaluate_table_straight(cards):
    pass
def evaluation(cards): #checks all combos
    ###             cheat sheet
    # check_pair returns cards, the pair amount and origin
    # straight returns highest card from table or hand
    #flush returns highest card  for flush
    #fullhouse returns nothing useful

    # evaluate_$combo = how close the table is getting to the combination
    #
    global risk;
    risk=10
    combo='none'
    pairamount=0
    pair=check_pair(cards)
    if not(pair == None):
        pairamount=len(pair)
        if(pairamount==1):
            combo="pair"
        else:
            if pair[0]['pairamount']==4 or pair[1]['pairamount']==4:#stops 2 pairs from overriding pair of 4
                combo="pair"

            else:
                combo="two pair"

    straight=check_straight(cards)
    if not(straight==None):
        combo='straight'
    flush=check_flush(cards)
    if not(flush==None):
        combo='flush'
    if pairamount >=2:
        fullhouse=check_fullhouse(pair)
        if not (fullhouse==None):
            combo='fullhouse'
    if combo=='pair' or combo=='two pair':
        rating_system(pair,combo,cards)
    elif combo=='straight':
        rating_system(straight,combo,cards)
    elif combo=='flush':
        rating_system(flush,combo,cards)
    elif combo=='fullhouse':
        rating_system('none',combo,cards)
    else:
        print('COMBO:no combo')
    ## checks possible combinations on table
    evaluate_table_flush(cards)
    #TODO:evaluate_table_straight (dunno how yet)

    
    return risk
test=evaluation([[{'type': 'kreicis', 'card': '10', 'rating': 8, 'origin': 'table'}
],[{'type': 'karavs', 'card': 'j', 'rating': 2, 'origin': 'table'}],
[{'type': 'karavs', 'card': '4', 'rating': 4, 'origin': 'hand'}],
[{'type': 'kreicis', 'card': 'a', 'rating': 3, 'origin': 'table'}],
[{'type': 'kreicis', 'card': '8', 'rating': 5, 'origin': 'table'}],
[{'type': 'kreicis', 'card': 'q', 'rating': 14, 'origin': 'table'}],
[{'type': 'karavs', 'card': '9', 'rating': 6, 'origin': 'hand'}]]) # fake data for testing purposes
print('risk level',test)
