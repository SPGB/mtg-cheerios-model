import random
from termcolor import colored

# Vars
deck = "list_expanded_1.txt"
library = []
battlefield = []
tapped = []

# Parses Library
def parseList(list):
  with open(list, "r") as ins:
    array = []
    for line in ins:
        array.append(line.strip())
    return array

def shuffle(library):
  random.shuffle(library)

# Draws from library
def draw(library, hand):
  if len(library) <= 1:
    return
  card = library[0]
  library.remove(card)
  hand.append(card)
  return card

# Returns all of one card to your hand
def bounceAll(item, hand):
  global battlefield
  global tapped
  battleFieldTemp = []
  for card in battlefield:
    if card == item:
      hand.append(card)
    else:
      battleFieldTemp.append(card)
  battlefield = battleFieldTemp

  tappedTemp = []
  for card in tapped:
    if card == item:
      hand.append(card)
    else:
      tappedTemp.append(card)
  tapped = tappedTemp
  return hand

# Draws the starting hand
def drawHand():
  global library
  global battlefield
  global tapped
  battlefield = []
  tapped = []
  library=parseList(deck)
  shuffle(library)
  hand = []
  handSize = 7
  isDrawing = True
  while isDrawing:
    hand = []
    for i in range(0,handSize):
      draw(library, hand)
    if handSize == 5:
      isDrawing = False
    if "engine" in hand and ("land" in hand or "fetchland" in hand) and "cheerio" in hand:
      isDrawing = False
    handSize -= 1
  return hand

# The mechanics of playing a card
def play(card, hand):
  hand.remove(card)
  battlefield.append(card)
  if card == "fetchland" and "land" in library:
    battlefield.remove("fetchland")
    library.remove("land")
    battlefield.append("land")
  if card == "engine":
    manaTap(2)
  if card == "serum":
    drawCard = draw(library, hand)
    battlefield.remove(card)
    manaTap(1)
    print "Drew", drawCard, "Next two cards:", library[0], library[1]
    for i in range(0, 1):
      scryCard = library[i]
      if scryCard in ["land", "fetchland", "mox opal"] and manaAvailable() >= 1:
        library.remove(scryCard)
        library.append(scryCard)
      if scryCard not in ["land", "fetchland", "mox opal"] and manaAvailable() < 2:
        library.remove(scryCard)
        library.append(scryCard)
      if scryCard == "erayo":
        library.remove(scryCard)
        library.append(scryCard)
      if battlefield.count("engine") > 2 and scryCard == "engine":
        library.remove(scryCard)
        library.append(scryCard)

  if card == "retract":
    hand = bounceAll("cheerio", hand)
    hand = bounceAll("mox opal", hand)
    battlefield.remove(card)
    manaTap(1)
  if card == "recall":
    hand = bounceAll("cheerio", hand)
    hand = bounceAll("mox opal", hand)
    battlefield.remove(card)
    manaTap(2)
  if card == "cheerio":
    draws = []
    for i in range(0, battlefield.count("engine")):
      draws.append(draw(library, hand))
    print ".. drew", draws
  return hand

# Main game loop
def game():
  hand = drawHand()
  turnNum = 0
  while battlefield.count("cheerio") < 10 and turnNum < 10:
    turnNum += 1
    turn(turnNum, hand)

  return turnNum

# Returns your mana available
def manaAvailable():
  global battlefield
  if "mox opal" in battlefield and battlefield.count("cheerio") >= 2:
    return battlefield.count("land") + 1
  else:
    return battlefield.count("land")

# Untaps your mana
def manaUntap():
  global tapped
  for card in tapped:
    battlefield.append(card)
  tapped = []

# Taps your mana
def manaTap(count):
  for i in range(0, count):
    if "land" in battlefield:
      battlefield.remove("land")
      tapped.append("land")
    elif "mox opal" in battlefield:
      battlefield.remove("mox opal")
      tapped.append("mox opal")

# Handles your turn logic
def turn(turnNum, hand):
  print colored('Turn ' + str(turnNum), 'green')
  print colored(hand, 'green')

  manaUntap()

  if turnNum > 1:
    drawCard = draw(library, hand)
    print "Drawing", drawCard

  if "fetchland" in hand:
    print "Playing fetchland"
    play("fetchland", hand)
  elif "land" in hand:
    print "Playing land"
    play("land", hand)

  turnMainPhase(turnNum, hand)

# Main phase of your turn
def turnMainPhase(turnNum, hand):
  if battlefield.count("cheerio") > 10:
    return

  elif "mox opal" in hand and "mox opal" not in battlefield:
    print "Playing Mox"
    play("mox opal", hand)
    turnMainPhase(turnNum, hand)

  elif "cheerio" in hand and "mox opal" in battlefield and manaAvailable() < 2:
    print "Playing cheerio (to activate mox)"
    play("cheerio", hand)
    turnMainPhase(turnNum, hand)

  elif "engine" in hand and battlefield.count("engine") < 4 and manaAvailable() >= 2:
    print "Playing engine. mana avail: ", manaAvailable()
    play("engine", hand)
    turnMainPhase(turnNum, hand)

  elif "serum" in hand and manaAvailable() >= 1 and len(library) > 2:
    print "Playing Serum"
    play("serum", hand)
    turnMainPhase(turnNum, hand)

  elif "cheerio" in hand and battlefield.count("engine") >= 2:
    print "Playing Cheerio"
    play("cheerio", hand)
    turnMainPhase(turnNum, hand)

  elif "cheerio" in hand and "engine" in battlefield and "engine" not in hand:
    print "Playing Cheerio (1eng)"
    play("cheerio", hand)
    turnMainPhase(turnNum, hand)

  elif "mox opal" in battlefield and hand.count("cheerio") >= 2 and turnNum > 3:
    play("cheerio", hand)
    play("cheerio", hand)
    turnMainPhase(turnNum, hand)

  elif "retract" in hand and battlefield.count("cheerio") > 0 and manaAvailable() >= 1:
    print "Playing retract"
    play("retract", hand)
    print "Hand", hand
    turnMainPhase(turnNum, hand)

  elif "recall" in hand and battlefield.count("cheerio") >= 2 and manaAvailable() >= 2:
    print "Playing recall"
    play("recall", hand)
    print "Hand", hand
    turnMainPhase(turnNum, hand)

# Average hand sizes that contain engine
handSizes = []
for i in range(0, 1000):
  hand = drawHand()
  handSizes.append(len(hand))

print "Hand size average:", sum(handSizes)/float(len(handSizes))

# Average turns until win
turnCounts = []
for i in range(0, 10000):
  turnCounts.append( game() )

print "Average turns:", sum(turnCounts)/float(len(turnCounts))