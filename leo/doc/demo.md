
# Leo's demo.py plugin

At present, these are more design docs than actual descriptions of reality.

## Overview

This plugin runs dynamic demos from Leo files.

A **script tree**, a tree of **demo scripts**, controls the demo. Pressing the space bar executes the next script in the tree. Demo scripts typically alter the outline, freeing the presenter from having to type correctly or remember sequences of desired actions. 

To run a demo, you create a **top-level script** that creates an instance of the Demo class. Top-level scripts are free to subclass the Demo class. The top-level script calls my_demo.start(p), where p is the root of the script tree. For example:

```python
import leo.plugins.demo as demo

class Demo1(demo.Demo):
    
    def setup(self, p):
        fn = 'c:/demos/demo1.leo'
        demo.user_d['c'] = g.openWithFileName(fn, old_c=c)

Demo1(c).start(g.findNodeInTree(c, p, 'demo1-commands'))
```

Demo scripts have access to the 'demo' variable, which is bound to the Demo instance. This allows demo scripts to use all the **helper methods** in the Demo class. These methods can:

- Animate typing in headlines, body text, the minibuffer, or anywhere else.
- Overlay a scaled image on the screen.
- Open any Leo menu, selecting particular menu items.
- Scale font sizes.
- Open another .leo file and present the demo in the new outline window.
- And many other things, as described below.

## The Demo class

The Demo class executes demo scripts and handles key handling during the demo.

The Demo class traps only the space-bar key (*or right-arrow key?*), passing all other keys to Leo's key-handling code. For example:

```python
    demo.single_key('Alt-X')
    demo.plain_keys('ins\\tno\\t\\n')
```

This executes the insert-node command!

## Helper methods

*These descriptions may change at any time, without notice*.

### Starting and stopping

**demo.setup(p)**: May be oeverriden in subclasses. Called before executing the first demo script.

**demo.start(p)**: Starts a demo, where p is the root of demo script tree. 

**demo.quit()**: Ends the demo and calls the teardown script. **Note**: The demo automatically quits after executing the last demo script.

**demo.teardown(p)**: May be oeverriden in subclasses. Called whenever the demo ends.

### Typing

**demo.body(s)**, **demo.log(s)** and **demo.tree(s)**: Creates a caption with text s in the indicated pane. A **caption** is a text area that overlays part of Leo's screen. By default, captions have a distinctive yellow background. The appearance of captions can be changed using Qt stylesheets. See below.

**demo.body_keys(s,n1=None,n2=None)**: Draws the string s in the body pane of the presently selected node. n1 and n2 give the range of delays to be inserted between typing. If n1 and n2 are both None, values are given that approximate a typical typing rate.

**demo.head_keys(s,n1=None,n2=None)**: Same as demo.body_keys, except that the keys are "typed" into the headline of the presently selected node.

**demo.plain_keys(s,n1=None,n2=None,pane='body')** Same as demo.body_keys, except that the keys are typed into the designated pane. The valid values for the 'pane' argument are 'body','log' or 'tree'.

**demo.single_key(setting)** generates a key event. Examples:
```python
   demo.single_key('Alt-X') # Activates the minibuffer
   demo.single_key('Ctrl-F') # Activates Leo's Find command
```
The 'setting' arg can be anything that would be a valid key setting. The following are equivalent: "ctrl-f", "Ctrl-f", "Ctrl+F", etc., but "ctrl-F" is different from "ctrl-shift-f".

### Commands

**demo.command(command_name)**: Executes the named command.

### Menus

**demo.open_menu(menu_name)**: Opens the menu whose name is given, ignoring case and any non-alpha characters in menu_name. This method shows all parent menus, so demo.open_menu('cursorback') suffices to show the "Cmds\:Cursor/Selection\:Cursor Back..." menu.

**demo.dismiss_menubar()**: Dismisses the menu opened with demo.open_menu.

### Images and overlays

**demo.image(pane,fn,center=None,height=None,width=None)**: Overlays an image in a pane:

- `pane`: One of  'body', 'log' or 'tree'.
- `fn`: The path to the image file, resolved to the leo/Icons directory if fn is a relative path.
- `height`: Scales the image so it is `height` pixels high.
- `width`: Scales the image i so it `width` pixels wide.
- `center`: True: center the image horizontally in the given pane.

### Focus

**demo.focus(pane)**: Forces focus to the given pane. Valid values are 'body', 'log' or 'tree'.

### Demo ivars

**demo.script_list**: Starting a demo "freezes" all demo scripts into this list.

**demo.user_d**: A Python dictionary that demo scripts may freely use.

**demo.index**: The index into demo.script_list of the *next* script to be executed.
## Style sheets

**Note**: Helper methods will likely exist to alter this stylesheet more easily.

Presenters may alter the appearance of captions by using changing the
following stylesheet::

```css
    QPlainTextEdit#democaption {
        background-color: yellow;
        font-family: DejaVu Sans Mono;
        font-size: 18pt;
        font-weight: normal; /* normal,bold,100,..,900 */
        font-style: normal; /* normal,italic,oblique */
    }
```

You will find this stylesheet in the node @data
``qt-gui-plugin-style-sheet`` in leoSettings.leo or myLeoSettings.leo.

## Acknowledgements

This plugin was inspired by [demo-it](https://github.com/howardabrams/demo-it/blob/master/demo-it.org). Or perhaps demo-it was inspired by Leo's earlier screencast plugin.
