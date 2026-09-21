# Domain Model Critique

## Over-Modelled
Claude over-modelled the filtering feature by creating a separate ItemFilter class. In my requirements, filtering is only an action users can perform on their wishlist items. I do not need to store filters as separate data, so I did not include an ItemFilter entity in my model.

## Under-Modelled
Claude under-modelled the category information for each item. My requirements
include saving items based on a category, but Claude did not include category
as an attribute of the Item class. Instead, category was placed in the
ItemFilter class. I included category directly in WISHLIST_ITEM because each
item needs to store which category it belongs to.
## Unsupported Relationships / Assumptions
Claude assumed that Wishlist needed a relationship with a separate ItemFilter
class. My requirements only state that users should be able to filter their
wishlist items. It does not  state that a filter needs to be stored or have its
own relationship with the wishlist. In my model, filtering can be performed
using the category, priority, and bought attributes already stored in
WISHLIST_ITEM. The app is simply looking through the existing WISHLIST_ITEM records and showing the ones that match the filter. Like if it was bought or not. Or High Priority OR not.
## What the AI Got Right
Claude correctly identified the main information that needs to be stored for
each wishlist item. It included the item's name, price, store, priority, and
bought status. These attributes match my requirements and are also included
in my WISHLIST_ITEM entity. Claude also correctly recognized that adding,
editing, deleting, marking items as bought.


## Why I Chose My Model
I chose my model because it is simpler and the main purpose of Dear
Wishlist is to store and manage wishlist items. I did not create separate entities for
features like filtering because those features can use the information that
is already stored for each item. This keeps my model focused on the
requirements I created for the app without adding unnecessary parts.
