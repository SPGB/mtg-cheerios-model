# MTG Cheeri0s simulator

Cheeri0s is a deck that mostly ignores what the opponent does in order to win. This is a simplified model to predict what effect changes in the decklist has on winrates.

# Example usage 

` python main.py -l list_expanded_2.txt -t 10000 `

# Arguments

> -l, --library

specifies the library path (filename)

> -d, --debug

enables debug mode

>-t, --turns

number of simulations to run. Defaults to 1000

# Winrate

We calculate the number it turns until:
- We have a storm count of 20
- We have two mana and a grapeshot

# Simplifications

We are working to eliminate the simplifications and make the model more accurate. Currently we assume:
- lands have no mana type
- all cheerios are the same
- all engines are the same

If you would like to improve the model, please make a pull request