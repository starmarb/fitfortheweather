Project Group 9: Philomena Wu, Sammi Kwon, Fatima Kamara
Project Name: 'Fit For The Weather

Motivation: 
    Create a virtual closet assistant to help users build and create their own outfits with items from their own closet that would be "fit for the weather." 
    *As we don't monitor what user's upload, items aren't limited to just their own closet. In fact, we imagine the website could also be used to help user's come up with their own style and visualize their ideal outfits/closet and be be smart with their decision to buy a clothing item they might be interested in but might not work with current items in their own closet.

Main features:

Login/Sign up:
    -Checks for existing usernames
    -Stores user's data and displays information for their personal closet which they can edit

Homepage:
    -Using a weather API, the website's homepage displays clothing items recommended for the day's weather/current temperature
    (recommend items include those that would be good for layering with others). We use a function, temperature.py, that uses the data from the Weather API and, depending on if it's a piece of outerwear or a top or one-piece, it will output them to allow the possibility of layering warmer outer wear with colder tops or one-pieces.
    -Displays clothing items in different categories in the following order: outerwears, one-pieces, tops, bottoms so users can visualize what outfits they can make (horizontal scroll bar for each row to mix-and-match items)
    -Users can select 1 item for their row(s) of choice, create a name for that outfit, and save it

Closet:
    -Users can upload an image of a clothing item (with a valid image file), add a short description/name, select when they typically wear the clothing item, and pick and add color(s) to tag the item with HTML Color Picker.
        - The colors are saved as HEX codes that are saved and queried in the database along with other descriptions.
    -Similar to the homepage, displays all closet up in 4 rows/categories (outerwears, one-pieces, tops, bottoms)
    -User can remove items
    -User can select as many colors to filter the closet by and display only those clothing items that were tagged with those color(s) (great for styling by color pallete/shades (e.g. pastel colors, neon, etc))

Outfits:
    -Displays all user-saved outfits "fit for the weather" alongside the outfit's name
    -Items within an outfit are ordered vertically (similar to the UI of the hompage and closet) for ease of visualizing how the items look together in the outfit
    -User can remove outfits

Logout:
    -Logs user out from the session
