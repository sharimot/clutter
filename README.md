# Clutter: The Minimalist Notebook

Clutter is a minimalist note-taking and task management tool that relies on a single text file called clutter.txt.
Clutter selects and displays lines from clutter.txt based on your query.
While this may sound simple, it's an incredibly powerful idea that could potentially transform how we organize and access information.

## Use cases

- Notebook
- Task management
- Calendar
- File management
- Diary
- Bookmark

## Get started

### Web version (demo)

Please visit <https://sharimot.github.io/clutter/>.

Using the demo version forever is not recommended for the following reasons:

- It could get hacked and could leak your private information.
- There is a restriction on the size of the data storage.
- Syncing and backing up your data might not be easy.

So please use it to understand what it feels like to use Clutter.

In the web version, clutter.txt refers to the contents of your data that is stored in the browser.
To get clutter.txt, click on the `[get]` button.
To set clutter.txt, click on the `[set]` button.

### CLI version (main)

Before you begin, make sure you have python3 and pip installed on your system.

Clutter uses a plain text file called clutter.txt as its database file.
To get started, create an empty text file and name it clutter.txt.

To install and run Clutter, follow these steps:

1. Clone the repository from GitHub:

```bash
git clone https://github.com/sharimot/clutter
```

2. Change into the project directory:

```bash
cd clutter
```

3. Install the required dependencies:

```bash
python3 -m pip install -r requirements.txt
```

4. Run Clutter, specifying the path to clutter.txt:

```bash
python3 clutter.py /path/to/clutter.txt
```

Be sure to replace `/path/to/clutter.txt` with the actual path to your clutter.txt file.

Once Clutter is running, you can access it at <http://localhost:12224>.

Why port number 12224?
Because:

```python
12224 == int(hashlib.sha256('clutter'.encode('utf-8')).hexdigest()[:4], 16)
```

If you prefer, you can specify a different port number (e.g., 9999) when running Clutter:

```bash
python3 clutter.py /path/to/clutter.txt 9999
```

## Features

### Add

To add an item to clutter.txt, follow these steps:

1. Click on the invisible input field located in the second row, which is indicated by a plus sign.
2. Type a text you want to add.
Line breaks are not allowed.
3. Press Enter.

You will see that the item has been added to clutter.txt, with date and time automatically included in the format `yyyymmddHHMMSS`.

### Edit

To edit an item, follow these steps:

1. Click on the minus sign preceding the item you want to edit.
2. Make the necessary changes to it.
3. Press Enter to save your edits.

### Find

To search for items, use the invisible input field in the top row, which is indicated by an equal sign.
When you search for a specific string (e.g., `hello`), only the items that contain the string (case-insensitive) will be shown.
The letter case is ignored, which means that searching with `hello` will return the same result as searching with `hElLo`.

To search for items that contain multiple strings, (e.g., `hello` and `world`), simply type both strings separated by a space.
For example, searching with `hello world` will return items that contain both `hello` and `world`.

To search for items that contain a specific phrase (e.g., `hello world`), replace the space with `[space]`.
For example, searching with `hello[space]world` will return items that contain the exact phrase `hello world` (with a space between `hello` and `world`)

To search for items that do not contain a string, use the `N` operator.
For example, searching with `hello Nworld` will return items that contain `hello` but do not contain `world`.

The number of items that match your search query will be displayed at the top left corner.
Clutter displays a maximum of 1000 items.
If there are more than 1000 items that match your search, the rest will be hidden.

### Sort

To sort the items, you can use the `A` or `D` prefixes before your search keywords.
`A` stands for ascending order, and `D` stands for descending order.
The sorting is based on the string after the keyword prefixed by `A` or `D`.

For example, if the search result for `hello` is:

```
20200101000000 Hello, world
20210101000000 hello world
20220101000000 hello world!
```

The search result for `Ahello` will be:

```
20210101000000 hello world
20220101000000 hello world!
20200101000000 Hello, world
```

When the search query is `Nquick brown Dfox Njumps`, Clutter will show items that do not contain `quick`, contain `brown`, contain `fox`, and do not contain `jumps`, and it will sort them by the string after `fox` in descending order.

### Swap

You can use Clutter to perform find and replace (aka substitute) operations.
To replace `source` with `target`, search with `S|source|target|` and then click on the `swap` button on the left.
Unlike find, the `source` and `target` of a swap query are *case-sensitive*.
You can use any separators other than `|`.
For example, to replace `hello|world` with `Hello|World`, you can search with `S/hello|world/Hello|World/` .

You can also add conditions to a swap query.
For example, to replace `source` with `target` only in items that contain `hello` but do not contain `world`, search with `S|source|target| hello Nworld`.
To replace a space character, use `[space]`.
For example, to replace `hello world` (with a space between `hello` and `world`) with `hello-world`, search with `S|hello[space]world|hello-world|`.

If you see a warning that says `"target" already exists!`, this means that the target is already present in clutter.txt.
You can click on the target and see what's there.
When the target is already present in clutter.txt, it may be difficult to redo the swap.
You can still perform such a swap, but you should be careful when doing so.

## Best practices

### Simplifying the command line

If you find it cumbersome to type out the command `python3 clutter.py /path/to/clutter.txt` repeatedly, you can create an alias to simplify it.

To do this, add the following line to your `~/.bashrc` file:
```bash
alias clutter-run="python3 /path/to/clutter.py /path/to/clutter.txt"
```

Then, you can simply run `clutter-run` to start Clutter.
This will save you time and make it easier to run Clutter from the command line.

### Vimium C: Clutter's best friend

It is highly recommended to use [Vimium C](https://chrome.google.com/webstore/detail/vimium-c-all-by-keyboard/hfjbmagddngcpeloejdejnfgbamkjaeg) to enhance your experience with Clutter.
Vimium C is a Chrome extension that allows you to navigate and interact with websites using only your keyboard.
It is an incredibly useful tool that can make using Clutter more efficient and convenient.

### Shortcuts

You can search items directly from the address bar.
For example, to search `hello`, type `http://localhost:12224/?q=hello` into the address bar.
You can also add items directly from the address bar.
For example, to add `hello`, type `http://localhost:12224/?add=hello` into the address bar.
Browsers like Chrome and Brave have options to set [site search shortcuts](https://support.google.com/chrome/answer/95426).
Use this feature to quickly search and add to Clutter.

### Tagging

In Clutter, you can use hashtags (e.g., "#tagname") and cashtags (e.g., "$tagname") to organize and categorize your items.
When you use these tags in your items, Clutter will colorize them to help you easily identify and distinguish them.

It is important to include a hashtag in every item you add to Clutter.
This helps you keep track of your items and makes it easier to search them.
However, you should avoid having too many items associated with a single tag.
This can make it difficult to manage your items and make it harder to find what you are looking for.
Instead, try to use a variety of tags to help you stay organized.

Every time you create a new tag, you should add an item like `#tag #newtagname #_`.
This allows you to easily search for all tag names by searching with `#tag`.

### Naming tags

To help you avoid confusion when using tags in Clutter, it is recommended to follow these guidelines for naming your tags:

- Use lowercase letters to make your tags easier to type.
- Use singular names to avoid confusion.
For example, use `#tag` instead of `#tags`.
- Avoid using tag names that are prefixes of other tag names.
For example, do not use both `#hello` and `#helloworld` as tags.
This can lead to confusion when searching, as searching with `#hello` will also return items with `#helloworld`.
Instead, consider using a name like `#hworld` for the `#helloworld` tag.

### Tag nesting

If you have a large number of tags, you can use tag nesting to help you stay organized.

For example, you could create a new sub-tag by adding an item like

`#tag #parent #child`

or

`#tag #grandparent #parent #child`

To view the list of tags, you can search for [`A#tag`](http://localhost:12224/?q=A%23tag).
This will show you the hierarchy of your tags and help you keep track of your organizational structure.

By using tag nesting, you can easily manage a large number of tags and keep your items organized.

### Timestamping

To easily copy and paste the current date and time (in the format yyyymmddHHMMSS), you can use automation tools like Karabiner-Elements, AutoHotKey, and AutoKey.

If you are a Mac user, you can achieve this by adding the following object into `profiles.complex_modifications.rules` of karabiner.json:

```json
{
    "description": "datetime",
    "manipulators": [
        {
            "from": {
                "key_code": "<your-favorite-letter>",
                "modifiers": {
                    "mandatory": [
                        "command"
                    ]
                }
            },
            "to": [
                {
                    "shell_command": "date +'%Y%m%d%H%M%S' | tr -d '\n' | pbcopy"
                }
            ],
            "type": "basic"
        }
    ]
}
```

Now, when you press the `command` key and `<your-favorite-letter>`, the current date and time will be copied to your clipboard.
You can then paste it as a timestamp.

### Task management

You can use tags to represent three different phases: `$todo`, `$done`, and `$trash`.
You can also combine these tags with timestamps to set deadlines (`$todo:yyyymmddHHMMSS`) or denote the completion time (`$done:yyyymmddHHMMSS`).
By following this convention, you can easily find and sort relevant tasks.

### Importance

To help you prioritize your items in Clutter, you can use carets (`^`) to signify their importance.
For example, you can use `^` to indicate that an item is important, and `^5` to indicate that an item is extremely important.

To sort your items by their importance, you can append `D^` to your search query.
This will show you the most important items first, helping you focus on the tasks that require your attention.

### Pagination

Pagination is not supported.
However, you can view old items by appending the year (`yyyy`) or month (`yyyymm`) to the search query.

### Home page

Pages like [`#tag D^`](http://localhost:12224/?q=%23tag+D^) and [`A$todo:`](http://localhost:12224/?q=A%24todo:) might be useful.

### Date search

As you can see, the date part of the timestamp on the left side of an item is clickable.
You can click on the date to see what happened on that day.

### File management

When it comes to organizing computer files, there are many different approaches to consider.
One method that can be effective is to name files using the format yyyymmddHHMMSS.extension and place them all in a single folder.
Once you have renamed a file, you can use Clutter to associate the file name with its description and category.

You can also apply the same principle to organize physical files.
By labeling a file with the format yyyymmddHHMMSS, taking a picture of it, sorting files by the timestamp, and then using Clutter to store this information, you will be able to easily locate the files you need later on.

### Multi-line texts

Clutter is not designed for writing multi-line texts.
If you need to write a long text, it is recommended that you use a text editor like Vim.
And when you're done writing, you can use Clutter to easily access them when you need them.

### Deleting an item

If you delete an item in Clutter, it's lost forever and can't be restored.
Using `$trash` is an alternative way to logically remove an item.

### Backup

You can back up clutter.txt by clicking on the equal sign in the top row.
The snapshot is stored in the `snapshots` folder as yyyymmddHHMMSS.clutter.txt.
(This feature is only available in the CLI version.)

### File synchronization

You can sync clutter.txt across multiple devices by using cloud storage services like Dropbox or Google Drive.

### Bookmarking

You can use browser extensions like Tampermonkey to easily check whether a page URL has already been included in clutter.txt.

Simply add the following script to Tampermonkey and customize the keybindings to your liking:

```javascript
// ==UserScript==
// @name         clutter
// @version      1.0.0
// @description  Easily search URLs.
// @author       sharimot
// @match        *://*/*
// @icon         https://raw.githubusercontent.com/sharimot/clutter/main/static/favicon.svg
// @grant        none
// ==/UserScript==

(function() {
    window.addEventListener('keydown', event => {
        if (event.target.matches('input')) { return; }
        if (event.target.matches('textarea')) { return; }
        if (event.target.closest('[contenteditable]')) { return; }
        const q = encodeURIComponent(location.href.split('#')[0]);
        const url = `http://localhost:12224/?q=${q}`;
        if (event.key === '<your-favorite-letter-1>') {
            window.location.href= url;
        }
        if (event.key === '<your-favorite-letter-2>') {
            window.open(url, '_blank').focus();
        }
    });
})();
```

With this script, you can press `<your-favorite-letter-1>` to open `http://localhost:12224/?q=<url>` in the same tab, or press `<your-favorite-letter-2>` to open `http://localhost:12224/?q=<url>` in a new tab.

You can press the plus button at the second row to automatically fill the input field with the text present in the above row.

### Time blocking

When you begin working on a new task, you can create an item like `#doit <task-name>`.
Once you have completed the task, you can create another item like `#done <task-name>`.
This can help clarify the context in which the item was added.
