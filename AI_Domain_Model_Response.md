Wishlist
+getItems() : List<Item>
+addItem(item: Item)
+editItem(itemId, price, store)
+deleteItem(itemId)
+markItemAsBought(itemId)
+filterItems(filter: ItemFilter) : List<Item>

-- arrow pointing downwards to below
contains - 

Item
-id
-name: String
-price: Decimal
-store: String
-priority: Priority
-isBought: Boolean

uses - 
ItemFilter
-priority: Priority
-isBought: Boolean

«enumeration»
Priority




Entities and how they trace to your requirements

Wishlist: holds all saved items (Stories 1, 2, 4). Its operations map to the stories: add (1), view (2), edit (3), delete (4), mark as bought (5), filter (6).
Item: has a name, price, store, and priority (Story 1). isBought comes from Stories 2 and 5. The id is a technical identifier so a specific item can be selected for editing, deleting, or marking as bought (Stories 3, 4, 5).
Priority: the value the user selects when adding an item (Story 1), also used for filtering (Story 6).
ItemFilter: represents the two filter options in Story 6, priority and bought/not bought. Each is optional, so the user can filter by one, both, or neither.

Decisions to be aware of

No User entity. Your requirements never mention accounts, login, or multiple users, so I modeled a single wishlist. If you add accounts later, a User would own a Wishlist.
Priority has no values. The requirements say the user can "select a priority" but don't say what the options are (Low/Medium/High, 1-5, and so on). I left the enumeration empty rather than invent them, so you'll want to define them.
Editing is limited to price and store, matching Story 3's acceptance criteria.
The non-functional requirements (2-second load, persistence, Chrome/Safari support) affect implementation rather than the domain, so they don't add entities. Persistence just means the Wishlist and its Items are stored between sessions.
