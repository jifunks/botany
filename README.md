# botany
![Screencap](http://tilde.town/~curiouser/botanybeta3.png)

by Jake Funke - jifunks@gmail.com - tilde.town/~curiouser - http://jakefunke.online/

A command line, realtime, community plant buddy.

You've been given a seed that will grow into a beautiful plant.
Check in and water your plant every 24h to keep it growing. 5 days without water = death. Your plant depends on you to live!

*"We do not 'come into' this world; we come out of it, as leaves from a tree." - Alan Watts*

*(work in progress)*

## getting started
botany is designed for unix-based systems. Clone into a local directory using `$ git clone https://github.com/jifunks/botany.git`.

Run with `$ python botany.py`.

*Note - botany.py must initially be run by the user who cloned/unzipped
botany.py - this initalizes the shared data file permissions.*

Water your seed to get started. You can come and go as you please and your plant continues to grow.

Make sure to come back and water every 24 hours or your plant won't grow.

If your plant goes 5 days without water, it will die!


## features
* Curses-based menu system, optimized for 80x24 terminal
* 20+ Species of plants w/ ASCII art for each
* Persistent aging system that allows your plant to grow even when app is closed
* Random and rare mutations can occur at any point in a plant's life
* SQLite Community Garden of other users' plants (for shared unix servers)
* Data files are created in the user's home (~) directory, along with a JSON file that can be used in other apps.
  * Data is created for your current plant and harvested plants

```
{
"description":"common singing blue seed-bearing poppy",
"file_name":"/Users/jakefunke/.botany/jakefunke_plant.dat",
"age":"0d:2h:3m:16s",
"score":1730,
"owner":"jakefunke",
"is_dead":false,
"last_watered":1489113197
}
```

### testing features
* ASCII art only shows first few stages of growth - more coming soon!

### to-dos
* Finish garden feature
  * Water neighbor's plants
* Harvest plant at end of life (gather seeds)
  * Plant pollination - cross-breed with neighbor plants to unlock second-gen plants
  * Share seeds with other users
* Global events
  * Server API to have rain storms, heat waves, insects
* Name your plant
* Reward for keeping plant alive
  * Hybridization, multiple generations, lineage tracking

## requirements
* Unix-based OS (Mac, Linux)
* Python 2.x
* Recommended: 80x24 minimum terminal, fixed-width font

## credits
* thank you tilde.town for inspiration!
* Thank you @etkirsch for [this gist](https://gist.github.com/etkirsch/53505478f53aeeac24a5) - python curses can be nightmarish!
