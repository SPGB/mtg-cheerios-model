import random
from termcolor import colored
import argparse
import re
import mana

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument("-l", "--library", help='The library path', required=True)
parser.add_argument("-d", "--debug", action='store_true', help='Enable Debug mode')
parser.add_argument("-t", "--turns", type=int, default=1000, help='Number of turns')
args = parser.parse_args()

if args is None:
  parser.print_help()
else:
  print(args)

# Vars
library = []
battlefield = []
tapped = []
stormCount = 0
landCount = 0

# Parses Library
def parseList(list):
  with open(list, "r") as ins:
    array = []
    pattern = re.compile("^([A-Za-z ]+)x([0-9]+)$")
    for line in ins:
      if pattern.match(line.strip()):
        match = re.search(pattern, line)
        for i in range(0, int(match.group(2))):
          array.append(match.group(1).strip())
      else:
        array.append(line.strip())
    return array

def shuffle(library):
  random.shuffle(library)

# Draws from library
def draw(library, hand):
  if len(library) == 0:
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
  global hand
  battlefield = []
  tapped = []
  library=parseList(args.library)

  if len(library) < 60:
    print "Library too small", len(library), library
    return null

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
    if "engine" in hand and mana.inHand(hand) > 0 and "cheerio" in hand:
      isDrawing = False
    handSize -= 1
  return hand

# The mechanics of playing a card
def play(card, hand):
  if args.debug: print "Playing", card, " | Mana Available", mana.available(battlefield, hand), " | Storm Count", stormCount
  global stormCount

  hand.remove(card)
  battlefield.append(card)

  if card is "fetchland" or card is "land":
    global landCount
    landCount += 1

  if card == "fetchland" and "land" in library:
    battlefield.remove("fetchland")
    library.remove("land")
    battlefield.append("land")
  else:
    stormCount += 1

  if card is "wraith":
    battlefield.remove("wraith")
    drawCard = draw(library, hand)
    if args.debug: print "..drew ", drawCard
  if card == "engine":
    mana.tap(2, battlefield, tapped, hand)
  if card == "serum":
    drawCard = draw(library, hand)
    battlefield.remove(card)
    mana.tap(1, battlefield, tapped, hand)
    scry(2)

  if card == "retract":
    hand = bounceAll("cheerio", hand)
    hand = bounceAll("mox opal", hand)
    battlefield.remove(card)
    mana.tap(1, battlefield, tapped, hand)
  if card == "recall":
    hand = bounceAll("cheerio", hand)
    hand = bounceAll("mox opal", hand)
    battlefield.remove(card)
    mana.tap(2, battlefield, tapped, hand)
  if card == "cheerio":
    draws = []
    for i in range(0, battlefield.count("engine")):
      draws.append(draw(library, hand))
    if args.debug and len(draws) > 0: print ".. drew", draws
  return hand

# Looks at the top cards on a library
def scry(scryNum):
  for i in range(0, scryNum - 1):
    scryCard = library[i]
    if args.debug: print "..scrying", scryCard
    if scryCard in ["land", "fetchland", "mox opal"] and mana.available(battlefield, hand) + mana.inHand(hand) >= 1:
      library.remove(scryCard)
      library.append(scryCard)
    if scryCard not in ["land", "fetchland", "mox opal"] and mana.available(battlefield, hand) + mana.inHand(hand) < 2:
      library.remove(scryCard)
      library.append(scryCard)
    if scryCard == "erayo":
      library.remove(scryCard)
      library.append(scryCard)
    if battlefield.count("engine") + hand.count("engine") > 2 and scryCard == "engine":
      library.remove(scryCard)
      library.append(scryCard)

# Main game loop
def game():
  if args.debug: print " "
  hand = drawHand()
  if len(hand) < 7:
    scry(1)
  turnNum = 0

  global stormCount
  global landCount

  while "grapeshot" not in battlefield and turnNum < 20:
    turnNum += 1
    stormCount = 0
    landCount = 0
    turn(turnNum, hand)

  return turnNum

# Handles your turn logic
def turn(turnNum, hand):
  if args.debug:
    print colored('Turn ' + str(turnNum), 'green')
    print colored(hand, 'green')

  # Upkeep: Untap
  mana.untap(tapped, battlefield)

  # Upkeep: draw
  if turnNum > 1:
    drawCard = draw(library, hand)
    if args.debug: print "Drawing", drawCard

  # Mainphase
  turnMainPhase(turnNum, hand)

def isCheerio(card):
  return card is "cheerio" or card is "paradise mantle"

# Main phase of your turn
def turnMainPhase(turnNum, hand):
  if stormCount > 20 and "grapeshot" in hand:
    play("grapeshot", hand)
  elif landCount is 0 and "fetchland" in hand:
    play("fetchland", hand)
    turnMainPhase(turnNum, hand)
  elif landCount is 0 and "land" in hand:
    play("land", hand)
    turnMainPhase(turnNum, hand)
  elif "mox opal" in hand and "mox opal" not in battlefield:
    play("mox opal", hand)
    turnMainPhase(turnNum, hand)

  elif "engine" in hand and battlefield.count("engine") < 4 and mana.available(battlefield, hand) >= 2:
    play("engine", hand)
    turnMainPhase(turnNum, hand)

  elif "serum" in hand and mana.available(battlefield, hand) >= 1 and len(library) > 2:
    play("serum", hand)
    turnMainPhase(turnNum, hand)

  elif "cheerio" in hand and battlefield.count("engine") >= 2:
    play("cheerio", hand)
    turnMainPhase(turnNum, hand)

  elif "cheerio" in hand and "engine" in battlefield and "engine" not in hand:
    play("cheerio", hand)
    turnMainPhase(turnNum, hand)

  elif "mox opal" in battlefield and battlefield.count("cheerio") < 2 and hand.count("cheerio") >= 2 and "engine" in hand and mana.available(battlefield, hand) < 2:
    if args.debug: print ".. attempting to turn on mox"
    play("cheerio", hand)
    play("cheerio", hand)
    turnMainPhase(turnNum, hand)

  elif "retract" in hand and battlefield.count("cheerio") > 0 and mana.available(battlefield, hand) >= 1:
    play("retract", hand)
    turnMainPhase(turnNum, hand)

  elif "recall" in hand and battlefield.count("cheerio") > 0 and mana.available(battlefield, hand) >= 2:
    play("recall", hand)
    turnMainPhase(turnNum, hand)

  elif "wraith" in hand:
    play("wraith", hand)
    turnMainPhase(turnNum, hand)

# Average hand sizes that contain engine
handSizes = []
for i in range(0, 1000):
  hand = drawHand()
  handSizes.append(len(hand))

print "Hand size average:", sum(handSizes)/float(len(handSizes))

# Average turns until win
turnCounts = []
for i in range(0, args.turns):
  turnCounts.append( game() )

print "Simulating", args.turns, "Average turns to win:", sum(turnCounts)/float(len(turnCounts))
for i in range(0, 20):
  if turnCounts.count(i) > 0:
    print "Turn", i,  100 * turnCounts.count(i) / float(args.turns), "%"

