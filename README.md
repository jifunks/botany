# botany

by Jake Funke - jifunks@gmail.com - tilde.town/~curiouser -
http://jakefunke.online/

A command line, realtime, community plant buddy.

You've been given a seed that will grow into a beautiful plant.
Check in and water your plant every 24h to keep it growing. 5 days without water = death. Your plant depends on you to live!

*(work in progress)*

## getting started
botany is designed for unix-based systems. Clone into a local directory using `git clone https://github.com/jifunks/botany.git`. Run with `python botany.py`. Water your seed to get started. You can come and go as you please and your plant continues to grow. Make sure to come back and water every 24 hours or your plant won't grow. If your plant goes 5 days without water, it will die!

## features
* Beautiful curses-based menu system
* Persistent aging system that allows your plant to grow even when app is closed
* Community leaderboard (for shared unix servers) created in program directory `garden_file.json`
* Data file is created in your home (~) directory, along with a JSON file that you can use in your own apps.
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

###testing features
* *In current alpha status, you can kill your plant with the kill command. This is permanent!*
* *Plant lifecycle is currently extremely short for testing - bear with me!*

###to-dos
* Add ASCII plant display
* Add plant inspection ('look' function)
* Finish garden display ('garden' function)
 * Allows you to water neighbor's plants
* Plant end of life (seeding/pollination
 * Plant pollination - cross-breed with neighbor plants to unlock second-gen plants
* Global events
 * Server API to have rain storms, heat waves, insects


## requirements
* Unix-based OS (Mac, Linux)
* Python 2.x

## credits
* thank you tilde.town for inspiration!
* Thank you @etkirsch for [this gist](https://gist.github.com/etkirsch/53505478f53aeeac24a5) - python curses can be nightmarish!
