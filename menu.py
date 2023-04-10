# modified from: https://stackoverflow.com/questions/39488788/how-to-make-a-menu-in-python-navigable-with-arrow-keys

import curses

def menu(stdscr, classes, message):
  """A method to create the curses menu UI for our chat service menus"""
  
  # visual design details for menu
  attributes = {}
  curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
  attributes['normal'] = curses.color_pair(1)

  curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
  attributes['highlighted'] = curses.color_pair(2)

  c = 0  # last character read
  option = 0  # the current option that is marked
  while True:  # Enter in ascii
    stdscr.erase()
    stdscr.addstr(message)
    for i in range(len(classes)):
      if i == option:
        attr = attributes['highlighted']
      else:
        attr = attributes['normal']
      stdscr.addstr("{0}".format(" > "))
      stdscr.addstr(classes[i] + '\n', attr)
    c = stdscr.getch()
    if c == 10: # this means enter key has been pressed
      break
    elif c == curses.KEY_UP:
      if option == 0: # go back to bottom of list
        option = len(classes) - 1
      else:
        option -= 1
    elif c == curses.KEY_DOWN:
      if option == len(classes) - 1: # go back to top of list
        option = 0
      else:
        option += 1

  return classes[option]
