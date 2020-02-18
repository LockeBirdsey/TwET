# TwEGeT
Twine Executable Generator Tool  
(although it really works with any HTML based project)

![Screenshot of main TwEGeT window](./imgs/1.png "screenshot")

## Using TwEGeT?

## Why is TwEGeT?
Deploying Twine stories is usually dead simple (heck, they're HTML files).  
However, some stories are media rich and become a little more confusing to package.  
And of course, with lots of media, comes large file-sizes. But that is only 1 problem.
As time continues its course, web technologies change and occasionally certain things become obsolete, either by way of design or by accident.

Hosting a Twine story to access in a browser is a wonderful thing, but sometimes these technology changes make stories impossible to play in their original state.
As such, deploying a story in a static browser, prevents[^1] this from happening. 

Therefore, TwEGeT aims to solve 2 problems.

## What is TwEGeT?

It is a tool to simply generate distributable standalone executable files for uploading to wherever you see fit, e.g. itch.io, GameJolt, Steam

## How is TwEGeT?

TwEGeT is, in reality, a front-end, built in Python, to control some slightly annoying functionality when wanting to distribute Twine stories as standalone applications. 
Moreover, it is platform agnostic, which means you can build executables for the three main classes of systems. 

Python 3.6
 - All standard libraries, except:
 - GUI: PySimpleGUI
 
NPM/NPX
 - Electron Forge
 
 TweeGo


## Future
- Build executables for Steam
- Build executables for mobile (I.e. PhoneGap)
- Automated media importing and full directory creation
- Inevitable design changes

## Additional information
Posts on the design and purpose of TwEGeT:
1. (https://lockeb.dev/2020/02/16/yate-i-guess.html)

---
[^1]: It is possible that these will be made obsolete as well but this seems like a good solution right now.


