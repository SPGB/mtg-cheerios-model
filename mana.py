
# Returns your mana available
def available(battlefield, hand):
  manaModifier = 0
  if "mox opal" in battlefield and battlefield.count("cheerio") >= 2:
    manaModifier += 1

  if "simian" in hand:
    manaModifier += 1

  return battlefield.count("land") + manaModifier

# Returns your mana available
def inHand(hand):
  return hand.count("land") + hand.count("mox opal") + hand.count("simian")

# Untaps your mana
def untap(tapped, battlefield):
  for card in tapped:
    battlefield.append(card)
  tapped = []

# Taps your mana
def tap(count, battlefield, tapped, hand):
  for i in range(0, count):
    if "land" in battlefield:
      battlefield.remove("land")
      tapped.append("land")
    elif "mox opal" in battlefield and battlefield.count("cheerio") >= 2:
      battlefield.remove("mox opal")
      tapped.append("mox opal")
    elif "simian" in hand:
      if args.debug: print "discarding simian"
      hand.remove("simian")