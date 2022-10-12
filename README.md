# botany
![Screencap](https://tilde.town/~curiouser/botany.png)

by Jake Funke - jifunks@gmail.com - tilde.town/~curiouser - http://jakefunke.online/

A command line, realtime, community plant buddy.

You've been given a seed that will grow into a beautiful plant.
Check in and water your plant every 24h to keep it growing. 5 days without water = death. Your plant depends on you and your friends to live!

*"We do not 'come into' this world; we come out of it, as leaves from a tree." - Alan Watts*

## getting started
botany is designed for unix-based systems. Clone into a local directory using `$ git clone https://github.com/jifunks/botany.git`.

Run with `$ python3 botany.py`.

*Note - botany.py must initially be run by the user who cloned/unzipped botany.py - this initalizes the shared data file permissions.*

Water your seed to get started. You can come and go as you please and your plant continues to grow.

Make sure to come back and water every 24 hours or your plant won't grow.

If your plant goes 5 days without water, it will die! Recruit your friends to water your plant for you!

A once-weekly cron on clear_weekly_users.py should be set up to keep weekly visitors tidy.


## features
* Curses-based menu system, optimized for 80x24 terminal
* 20+ Species of plants w/ ASCII art for each
* Persistent aging system that allows your plant to grow even when app is closed
* Multiplayer! Water your friends plants & see who's visited your garden.
* Generations: each plant you bring to its full growth potential rewards you
  with 20% growth speed for the next plant
* Random and rare mutations can occur at any point in a plant's life
* SQLite Community Garden of other users' plants (for shared unix servers)
* Data files are created in the user's home (~) directory, along with a JSON file that can be used in other apps.
  * Data is created for your current plant and harvested plants

```
{
  "description":"common screaming mature jade plant",
  "generation":1,
  "file_name":"/home/curiouser/.botany/curiouser_plant.dat",
  "owner":"curiouser",
  "species":"jade plant",
  "stage":"mature",
  "age":"24d:2h:16m:19s",
  "rarity":"common",
  "score":955337.0,
  "mutation":"screaming",
  "last_watered":1529007007,
  "is_dead":false
}
```

### to-dos
* Plant pollination - cross-breed with neighbor plants to unlock second-gen plants
  * Share seeds with other users
* Global events
  * Server API to have rain storms, heat waves, insects
* Hybridization, lineage tracking

## requirements
* Unix-based OS (Mac, Linux)
* Python 3.x
* Recommended: 80x24 minimum terminal, fixed-width font

## credits
* thank you [tilde.town](http://tilde.town/) for inspiration!

## praise for botany
![Screencap](https://tilde.town/~curiouser/praise1.png)
![Screencap](https://tilde.town/~curiouser/praise2.png)
![Screencap](https://tilde.town/~curiouser/praise3.png)

